import logging

from app.config import get_settings


def get_logger(name: str) -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(settings.log_level)
    return logger


def safe_profile_for_logging(profile: dict) -> dict:
    """Drop nothing sensitive is collected in this app, but keep a single
    place to redact fields if the schema ever grows to include them."""
    redact_keys = {"aadhaar", "bank_account", "password", "otp"}
    return {k: v for k, v in profile.items() if k not in redact_keys}
