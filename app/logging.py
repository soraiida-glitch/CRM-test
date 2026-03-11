import logging
import sys
from typing import Any

import structlog

from app.request_context import request_id_var


def configure_logging(log_level: str) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            timestamper,
            structlog.processors.add_log_level,
            _inject_request_id,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def _inject_request_id(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    request_id = request_id_var.get()
    if request_id:
        event_dict.setdefault("request_id", request_id)
    return event_dict
