"""Sentry Configurations."""

from pydantic_settings import BaseSettings


class SentrySettings(BaseSettings):
    """Sentry setting for the application."""

    environment: str = ""
    sentry_dsn: str = ""
