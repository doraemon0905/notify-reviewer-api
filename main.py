# main.py

from fastapi import FastAPI, Request, HTTPException
import logging.config
import logging
from datetime import datetime
from app.routes.api import api_router
import hmac
import hashlib
import time
from app.config.settings import settings

logging.basicConfig(
    filename="app.log", level=logging.INFO, format="%(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI(title="Slack bot request review", debug=True)
app.include_router(api_router)


@app.middleware("http")
async def log_traffic(request: Request, call_next):
    start_time = datetime.now()
    request_body = await request.body()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    client_host = request.client.host
    log_params = {
        "request_method": request.method,
        "request_url": str(request.url),
        "request_size": request.headers.get("content-length"),
        "request_headers": dict(request.headers),
        "request_body": request_body.decode("utf-8"),
        "response_status": response.status_code,
        "response_size": response.headers.get("content-length"),
        "response_headers": dict(response.headers),
        "process_time": process_time,
        "client_host": client_host,
    }
    logger.info(log_params)
    return response


@app.middleware("http")
async def verify_slack_request(request: Request, call_next):
    slack_signature = request.headers.get("X-Slack-Signature")
    slack_request_timestamp = request.headers.get("X-Slack-Request-Timestamp")
    
    if not settings.slack_signing_secret:
        response = await call_next(request)
        return response

    if not slack_signature or not slack_request_timestamp:
        raise HTTPException(status_code=400, detail="Missing Slack signature or timestamp")

    # Prevent replay attacks by checking if the request timestamp is more than 5 minutes old
    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        raise HTTPException(
            status_code=400, detail="Request timestamp is too old"
        )

    request_body = await request.body()
    sig_basestring = f"v0:{slack_request_timestamp}:{request_body.decode('utf-8')}"
    my_signature = (
        "v0="
        + hmac.new(
            settings.slack_signing_secret.encode("utf-8"),
            sig_basestring.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(my_signature, slack_signature):
        raise HTTPException(status_code=400, detail="Invalid Slack signature")

    response = await call_next(request)
    return response
