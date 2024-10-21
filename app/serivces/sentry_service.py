"""Sentry service."""

import traceback
import types

import sentry_sdk
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

from app.config import SentrySettings, get_settings

DENY_LIST = [
    *DEFAULT_DENYLIST,
    "document_html",
    "document_url",
]

settings: SentrySettings = get_settings("sentry")


class SentryService:
    _instance: object = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def initialize():
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            send_default_pii=False,
            environment=settings.environment,
            before_send=SentryService._before_send,
            enable_tracing=True,
            event_scrubber=EventScrubber(denylist=DENY_LIST),
        )

    @staticmethod
    def capture_exception(exception):
        if sentry_sdk.Hub.current.client:
            if isinstance(exception, str):
                sentry_sdk.capture_message(exception)
            elif isinstance(exception, types.TracebackType):
                traceback_str = traceback.format_exc()
                sentry_sdk.capture_message(traceback_str)
            else:
                sentry_sdk.capture_exception(exception)

    @staticmethod
    def _before_send(event, _):
        if "logger" in event:
            return None

        if "extra" in event:
            SentryService._scrub_sensitive_data(event["extra"], DENY_LIST)

        if "exception" in event:
            for exception in event["exception"]["values"]:
                SentryService._scrub_exception(exception)

        return event

    @staticmethod
    def _scrub_sensitive_data(data, fields_to_scrub):
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key in fields_to_scrub:
                    data[key] = "[REDACTED]"
                else:
                    SentryService._scrub_sensitive_data(data[key], fields_to_scrub)
        elif isinstance(data, list):
            for item in data:
                SentryService._scrub_sensitive_data(item, fields_to_scrub)

    @staticmethod
    def _scrub_exception(exception):
        if "stacktrace" in exception:
            for frame in exception["stacktrace"]["frames"]:
                if "vars" in frame:
                    SentryService._scrub_sensitive_data(frame["vars"], DENY_LIST)
