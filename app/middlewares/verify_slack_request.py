from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from slack_sdk.signature import SignatureVerifier
from fastapi import HTTPException
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class VerifySlackRequest(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        slack_signature = request.headers.get("x-slack-signature")
        slack_request_timestamp = request.headers.get("x-slack-request-timestamp")

        if not settings.slack_signing_secret:
            response = await call_next(request)
            return response

        if not slack_signature or not slack_request_timestamp:
            raise HTTPException(
                status_code=400, detail="Missing Slack signature or timestamp"
            )

        verifier = SignatureVerifier(signing_secret=settings.slack_signing_secret)
        request_body = await request.body()

        # Add your verification logic here
        if not verifier.is_valid_request(
            request_body, slack_signature, slack_request_timestamp
        ):
            raise HTTPException(status_code=400, detail="Invalid Slack request")

        response = await call_next(request)
        return response
