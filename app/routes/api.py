"""All API Routers."""

from fastapi import APIRouter

from app.api import message

api_router = APIRouter()
api_router.include_router(
    message.router,
    prefix="/conversations",
    tags=["conversations"],
)
