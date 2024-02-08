import logging
from logging.config import dictConfig
from typing import Any, Dict

def initialize_logging() -> None:
    '''Initialize logging'''

    level = logging._nameToLevel.get(logging.INFO, logging.INFO)

    c = _robot_log_config(level)

    dictConfig(c)

class _LogBelow:
    def __init__(self, level: int) -> None:
        self._log_below_level = level

    def __call__(self, record: logging.LogRecord) -> bool:
        return record.levelno < self._log_below_level
    
def _robot_log_config(log_level: int) -> Dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "message_only": {"format": "%(message)s"},
        },
        "filters": {"records_below_warning": {"()": _LogBelow, "level": logging.WARN}},
        "handlers": {
            "unit_only": {
                "class": "systemd.journal.JournalHandler",
                "level": logging.DEBUG,
                "formatter": "message_only",
            },
            "syslog_plus_unit": {
                "class": "systemd.journal.JournalHandler",
                "level": logging.DEBUG,
                "formatter": "message_only",
                "SYSLOG_IDENTIFIER": "uvicorn",
            },
            "syslog_plus_unit_above_warn": {
                "class": "systemd.journal.JournalHandler",
                "level": logging.WARN,
                "formatter": "message_only",
                "SYSLOG_IDENTIFIER": "uvicorn",
            },
            "unit_only_below_warn": {
                "class": "systemd.journal.JournalHandler",
                "level": logging.DEBUG,
                "formatter": "message_only",
                "filters": ["records_below_warning"],
                "SYSLOG_IDENTIFIER": "uvicorn",
            },
        },
        "loggers": {
            "robot_server": {
                "handlers": ["syslog_plus_unit"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["syslog_plus_unit"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["syslog_plus_unit"],
                "level": log_level,
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["syslog_plus_unit"],
                "level": log_level,
                "propagate": False,
            },
            "starlette": {
                "handlers": ["syslog_plus_unit"],
                "level": log_level,
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["syslog_plus_unit_above_warn", "unit_only_below_warn"],
                # SQLAlchemy's logging is slightly unusual:
                # they set up their logger with a default level of WARN by itself,
                # so even if we enabled propagation, we'd have to override the level
                # to see things below WARN.
                # docs.sqlalchemy.org/en/14/core/engines.html#configuring-logging
                "level": log_level,
                "propagate": False,
            },
        },
    }