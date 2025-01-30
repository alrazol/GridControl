import structlog
import logging
import sys
from src.core.infrastructure.settings import Settings


# TODO: Fix DEBUG issues and improve config
def setup_logger():
    """Basic logger setup."""
    logging.basicConfig(
        level=getattr(logging, Settings().LOG_LEVEL, logging.INFO),
        format="%(message)s",
        stream=sys.stdout,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


logger = setup_logger()
