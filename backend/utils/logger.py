"""Structured logging for Multi-Agent NF-e System"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from config import settings


class StructuredLogger:
    """Structured logger that outputs JSON-formatted logs
    
    This logger provides structured logging with consistent formatting,
    making it easier to parse and analyze logs in production environments.
    """
    
    def __init__(self, name: str, level: Optional[str] = None):
        """Initialize structured logger
        
        Args:
            name: Logger name (typically module name)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   If None, uses settings.log_level
        """
        self.logger = logging.getLogger(name)
        self.name = name
        
        # Set log level
        log_level = level or settings.log_level
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup log handlers with JSON formatting"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.logger.level)
        
        # JSON formatter
        formatter = JsonFormatter()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _format_log_data(self, event: str, **kwargs) -> Dict[str, Any]:
        """Format log data as structured dictionary
        
        Args:
            event: Event name/description
            **kwargs: Additional context data
            
        Returns:
            Structured log data dictionary
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "logger": self.name,
            "event": event,
            "environment": settings.app_env,
        }
        
        # Add additional context
        if kwargs:
            log_data["context"] = kwargs
        
        return log_data
    
    def debug(self, event: str, **kwargs):
        """Log debug message
        
        Args:
            event: Event description
            **kwargs: Additional context
        """
        log_data = self._format_log_data(event, **kwargs)
        self.logger.debug(json.dumps(log_data))
    
    def info(self, event: str, **kwargs):
        """Log info message
        
        Args:
            event: Event description
            **kwargs: Additional context
        """
        log_data = self._format_log_data(event, **kwargs)
        self.logger.info(json.dumps(log_data))
    
    def warning(self, event: str, **kwargs):
        """Log warning message
        
        Args:
            event: Event description
            **kwargs: Additional context
        """
        log_data = self._format_log_data(event, **kwargs)
        self.logger.warning(json.dumps(log_data))
    
    def error(self, event: str, **kwargs):
        """Log error message
        
        Args:
            event: Event description
            **kwargs: Additional context (can include exception info)
        """
        log_data = self._format_log_data(event, **kwargs)
        self.logger.error(json.dumps(log_data))
    
    def critical(self, event: str, **kwargs):
        """Log critical message
        
        Args:
            event: Event description
            **kwargs: Additional context
        """
        log_data = self._format_log_data(event, **kwargs)
        self.logger.critical(json.dumps(log_data))
    
    def exception(self, event: str, exc: Exception, **kwargs):
        """Log exception with full traceback
        
        Args:
            event: Event description
            exc: Exception object
            **kwargs: Additional context
        """
        log_data = self._format_log_data(
            event,
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            **kwargs
        )
        self.logger.exception(json.dumps(log_data))
    
    def log_event(self, level: str, event: str, **kwargs):
        """Log event at specified level
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            event: Event description
            **kwargs: Additional context
        """
        log_method = getattr(self, level.lower(), self.info)
        log_method(event, **kwargs)
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """Log API request with standard format
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional context
        """
        self.info(
            "api_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_agent_action(
        self,
        agent_name: str,
        action: str,
        success: bool,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """Log agent action with standard format
        
        Args:
            agent_name: Name of the agent
            action: Action performed
            success: Whether action was successful
            duration_ms: Action duration in milliseconds
            **kwargs: Additional context
        """
        log_data = {
            "agent_name": agent_name,
            "action": action,
            "success": success,
        }
        
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
        
        log_data.update(kwargs)
        
        if success:
            self.info("agent_action", **log_data)
        else:
            self.error("agent_action_failed", **log_data)
    
    def log_database_query(
        self,
        query_type: str,
        table: Optional[str] = None,
        duration_ms: Optional[float] = None,
        rows_affected: Optional[int] = None,
        **kwargs
    ):
        """Log database query with standard format
        
        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, etc.)
            table: Table name
            duration_ms: Query duration in milliseconds
            rows_affected: Number of rows affected
            **kwargs: Additional context
        """
        log_data = {
            "query_type": query_type,
        }
        
        if table:
            log_data["table"] = table
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
        if rows_affected is not None:
            log_data["rows_affected"] = rows_affected
        
        log_data.update(kwargs)
        
        self.debug("database_query", **log_data)
    
    def log_batch_processing(
        self,
        job_id: str,
        status: str,
        total_files: int,
        processed: int,
        successful: int,
        failed: int,
        **kwargs
    ):
        """Log batch processing status with standard format
        
        Args:
            job_id: Batch job ID
            status: Job status
            total_files: Total number of files
            processed: Number of files processed
            successful: Number of successful imports
            failed: Number of failed imports
            **kwargs: Additional context
        """
        self.info(
            "batch_processing",
            job_id=job_id,
            status=status,
            total_files=total_files,
            processed=processed,
            successful=successful,
            failed=failed,
            **kwargs
        )


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for log records"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON
        
        Args:
            record: Log record
            
        Returns:
            JSON-formatted log string
        """
        # If message is already JSON, return as-is
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # If not JSON, create structured log
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)


# Global logger cache
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str, level: Optional[str] = None) -> StructuredLogger:
    """Get or create a structured logger
    
    Args:
        name: Logger name (typically __name__)
        level: Optional log level override
        
    Returns:
        StructuredLogger instance
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, level)
    return _loggers[name]


# Configure root logger
def configure_logging():
    """Configure root logging settings"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("crewai").setLevel(logging.INFO)


# Initialize logging on module import
configure_logging()
