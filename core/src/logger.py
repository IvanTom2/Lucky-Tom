import sys
import logging
from typing import Protocol
from typing import Any

import structlog
from structlog import BoundLogger


class ILogger(Protocol):
    def debug(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    def exception(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    def bind(self, *args: Any, **kwargs: Any) -> "ILogger": ...


def setup_logging(log_level: int = logging.INFO):
    # 1. Список процессоров, общих для всех режимов
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            (
                structlog.dev.ConsoleRenderer()
                if sys.stderr.isatty()
                else structlog.processors.JSONRenderer()
            ),
        ],
        # Настройка обертки логгера
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


setup_logging(log_level=logging.DEBUG)
logger: BoundLogger = structlog.get_logger()
