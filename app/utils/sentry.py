import contextlib

from app.serivces.sentry_service import SentryService

def capture_exception(exception):
    sentry_sdk = SentryService()
    with contextlib.suppress(Exception):
        sentry_sdk.initialize()
    sentry_sdk.capture_exception(exception)
