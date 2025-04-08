"""
logger.py

This module provides the `RedNeckLogger` class for creating and managing loggers with support for multiple logging streams, including console, CloudWatch, and file-based logging. The logger can be configured using a `config` dictionary or the `LOG_CONFIG` environment variable.
"""

from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from watchtower import CloudWatchLogHandler
import os
import json
import boto3
from botocore.exceptions import ClientError


class ColorFormatter(logging.Formatter):
    """Custom log formatter with colorized output based on log level."""
    COLORS = {
        "DEBUG": "\033[92m",  # Green
        "INFO": "",           # Default terminal text color
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, fmt, use_color=True):
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record):
        if self.use_color:
            log_color = self.COLORS.get(record.levelname, self.RESET)
            formatted_message = super().format(record)
            # Wrap the entire log message in the color
            return f"{log_color}{formatted_message}{self.RESET}"
        else:
            return super().format(record)


class RedNeckLogger:
    def __init__(self, log_name, streams=None, level="INFO", config=None):
        """
        Initialize the RedNeckLogger.

        Args:
            log_name (str): The base name for the log stream (e.g., "auth_service").
            streams (list): List of logging streams (e.g., ["console", "file", "cloudwatch"]).
            level (str): Logging level (e.g., "INFO", "DEBUG").
            config (dict): Optional configuration dictionary.
        """
        # Use the passed config, or extract from LOG_CONFIG, or create a default config
        if config:
            self.config = config
        else:
            config_env = os.getenv("LOG_CONFIG")
            if config_env:
                try:
                    self.config = json.loads(config_env)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON in LOG_CONFIG environment variable.")
            else:
                self.config = {
                    "log_group_name": "Default/Group",
                    "streams": ["console"],
                    "level": level,
                    "debug": False,
                    "file": {
                        "path": "./logs",
                        "max_bytes": 10 * 1024 * 1024,  # 10 MB
                        "backup_count": 5
                    },
                    "log_reset": False
                }

        # Extract configuration values, with environment variables taking precedence
        self.logger = None
        self.level = "DEBUG" if os.getenv("DEBUG_MODE", "false").lower() == "true" else os.getenv("LOG_LEVEL", self.config.get("level", level))
        self.streams = streams or self.config.get("streams", ["console"])
        self.log_reset = os.getenv("LOG_RESET", str(self.config.get("log_reset", False))).lower() == "true"

        # Handle APP_ENV for log group name
        app_env = os.getenv("APP_ENV", "Unknown")
        app_env = app_env.capitalize()

        # Append APP_ENV to log_group_name
        log_group_name = os.getenv("CLOUDWATCH_GROUP_NAME", self.config.get("log_group_name"))
        self.log_group_name = f"{log_group_name}/{app_env}"
        self.base_log_stream_name = log_name
        self.log_stream_name = self._generate_stream_name()
        self.stream_creation_date = datetime.now()
        self.stream_duration = int(os.getenv("CLOUDWATCH_STREAM_DURATION", 7))

    def setup_logger(self):
        """
        Set up the logger based on the configuration.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if self.logger:
            return self.logger

        # Create a logger
        self.logger = logging.getLogger(self.base_log_stream_name)
        self.logger.setLevel(self.level)

        # Delete the log stream if log_reset is True
        if self.log_reset:
            print("[RedNeckLogger] Resetting log stream...")
            self._delete_log_stream()

        # Define the custom log format
        log_format = '%(asctime)s %(levelname)s %(name)s: %(message)s [%(filename)s:%(lineno)d]'

        # Add handlers based on the configuration
        if "console" in self.streams:
            self._add_console_handler(ColorFormatter(log_format, use_color=True))
        if "cloudwatch" in self.streams:
            self._add_cloudwatch_handler(ColorFormatter(log_format, use_color=False))
        if "file" in self.streams:
            self._add_file_handler(ColorFormatter(log_format, use_color=False))

        return self.logger

    def _add_console_handler(self, formatter):
        """Add a console handler for local debugging."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _add_cloudwatch_handler(self, formatter):
        """Add a CloudWatch handler for logging to AWS CloudWatch."""
        try:
            self.logger.debug(f"Initializing CloudWatchLogHandler with log group: {self.log_group_name}, stream: {self.log_stream_name}")
            cloudwatch_handler = CloudWatchLogHandler(
                log_group=self.log_group_name,
                stream_name=self.log_stream_name
            )
            cloudwatch_handler.setLevel(self.level)
            cloudwatch_handler.setFormatter(formatter)
            self.logger.addHandler(cloudwatch_handler)

            self.logger.debug("CloudWatchLogHandler initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize CloudWatchLogHandler: {e}")

    def _add_file_handler(self, formatter):
        """Add a file handler for logging to a file."""
        file_config = self.config.get("file", {})
        log_folder = file_config.get("path", "./logs")
        max_bytes = file_config.get("max_bytes", 10 * 1024 * 1024)
        backup_count = file_config.get("backup_count", 5)

        log_folder = os.path.join(log_folder, self.log_group_name.replace("/", os.sep))

        # Reset log files if log_reset is True
        if self.log_reset:
            print(f"[RedNeckLogger] Resetting log files in {log_folder}...")
            if os.path.exists(log_folder):
                for file in os.listdir(log_folder):
                    file_path = os.path.join(log_folder, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

        os.makedirs(log_folder, exist_ok=True)

        file_path = os.path.join(log_folder, f"{self.log_stream_name}.log")
        try:
            file_handler = RotatingFileHandler(
                file_path, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.error(f"Failed to initialize RotatingFileHandler: {e}")

    def _generate_stream_name(self):
        """Generate a log stream name with the current date."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return f"{self.base_log_stream_name}-{current_date}"

    def _delete_log_stream(self):
        """Delete the log stream if it exists."""
        print(f"[RedNeckLogger] Attempting to delete log stream: {self.log_stream_name}")
        session = boto3.Session()
        client = session.client("logs", region_name=os.getenv("AWS_REGION", "us-east-1"))
        try:
            client.delete_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name
            )
            print(f"[RedNeckLogger] Log stream {self.log_stream_name} deleted successfully.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"[RedNeckLogger] Log stream {self.log_stream_name} does not exist.")
            else:
                print(f"[RedNeckLogger] Failed to delete log stream: {e}")


# Usage example
def get_logger(log_name=None, streams=["console"], level="INFO", config=None):
    logger = RedNeckLogger(log_name=log_name, streams=streams, level=level, config=config)
    return logger.setup_logger()