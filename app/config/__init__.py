from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from app.config.settings import Settings
from app.config.sentry import SentrySettings

load_dotenv()

settings: dict[str, type[BaseSettings]] = {
    "settings": Settings,
    "sentry": SentrySettings,
}


@lru_cache
def get_settings(app_type="app") -> Any:
    config_class = settings.get(app_type)

    if not config_class:
        raise TypeError(f"Configurations not found for: {app_type}")

    return config_class()


__all__ = [
    "Settings",
    "SentrySettings",
    "get_settings",
]
