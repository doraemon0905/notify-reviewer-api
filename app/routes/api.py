"""All API Routers."""

from fastapi import APIRouter
from app.api import message
from app.middlewares.verify_slack_request import VerifySlackRequest

api_router = APIRouter()
conversation_router = APIRouter()
conversation_router.include_router(
    message.router,
    prefix="/conversation",
    tags=["conversation"],
)
conversation_router.middleware("http")(VerifySlackRequest)
api_router.include_router(conversation_router)
