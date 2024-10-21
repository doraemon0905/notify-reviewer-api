# main.py

from fastapi import FastAPI, Request, HTTPException
import logging.config
import logging
from datetime import datetime
from app.routes.api import api_router
from slack_sdk.signature import SignatureVerifier
from app.config.settings import settings

logging.basicConfig(
    filename="app.log", level=logging.INFO, format="%(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI(title="Slack bot request review", debug=False)
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
    slack_signature = request.headers.get("x-slack-signature")
    slack_request_timestamp = request.headers.get("x-slack-request-timestamp")

    if not settings.slack_signing_secret or not request.url.path.startswith(
        "/conversation"
    ):
        response = await call_next(request)
        return response

    if not slack_signature or not slack_request_timestamp:
        raise HTTPException(
            status_code=400, detail="Missing Slack signature or timestamp"
        )
    verifier = SignatureVerifier(signing_secret=settings.slack_signing_secret)
    request_body = await request.body()

    if not verifier.is_valid(
        body=request_body, timestamp=slack_request_timestamp, signature=slack_signature
    ):
        raise HTTPException(status_code=400, detail="Invalid Slack signature")

    response = await call_next(request)
    return response
