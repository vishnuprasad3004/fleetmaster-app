"""Structured JSON Logging configuration for FleetMaster."""

import os
import logging
import logging.handlers
from pythonjsonlogger import jsonlogger
from app.config.settings import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON log formatter to inject custom fields."""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        log_record['environment'] = settings.ENV
        log_record['logger'] = record.name


def setup_logging():
    """Setup and return root logger with stream and rotating file handlers."""
    # Define log directory
    log_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "logs")
    )
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "fleetmaster.log")

    # Get root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid double logging
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    root_logger.setLevel(log_level)

    # Define JSON formatter
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d'
    )

    # 1. Console Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)
    stream_handler.setLevel(log_level)
    root_logger.addHandler(stream_handler)

    # 2. Rotating File Handler (Max 10MB per file, keeping 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)  # Store INFO level and above to file
    root_logger.addHandler(file_handler)

    # Prevent uvicorn logs from duplicating or using default handler
    for uvicorn_logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uv_logger = logging.getLogger(uvicorn_logger_name)
        uv_logger.handlers = []
        uv_logger.propagate = True

    logging.info("Structured logging initialized", extra={"log_file": log_file_path})


# Initialize logging
setup_logging()
logger = logging.getLogger("fleetmaster")


def log_audit(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    company_id: Optional[str] = None,
    status: str = "success",
    details: Optional[dict] = None
):
    """Log structured audit event."""
    audit_logger = logging.getLogger("fleetmaster.audit")
    extra = {
        "audit": True,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "user_id": user_id,
        "company_id": company_id,
        "status": status,
        **(details or {})
    }
    audit_logger.info(f"Audit log: {action} on {resource_type}", extra=extra)
