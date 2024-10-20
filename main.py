# main.py

from fastapi import FastAPI, Request
import logging.config
import logging
from datetime import datetime
from app.routes.api import api_router

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')
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
        "client_host": client_host
    }
    logger.info(log_params)
    return response
