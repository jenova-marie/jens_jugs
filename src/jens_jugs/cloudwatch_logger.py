import logging
from watchtower import CloudWatchLogHandler
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError

class CloudWatchLogger:
    def __init__(self, log_group_name, log_stream_name, level=logging.INFO):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        # Set the log level based on debug_mode
        self.debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        self.level = logging.DEBUG if self.debug_mode else level
        self.logger = None

    def setup_logger(self, reset_log_stream=False):
        if self.logger:
            print("[CloudWatchLogger] Logger already initialized.")
            return self.logger

        print(f"[CloudWatchLogger] Initializing logger for log group: {self.log_group_name}, log stream: {self.log_stream_name}")

        # Delete the log stream if reset_log_stream is True
        if reset_log_stream:
            print("[CloudWatchLogger] Resetting log stream...")
            self._delete_log_stream()

        # Create a logger
        self.logger = logging.getLogger(self.log_stream_name)
        self.logger.setLevel(self.level)
        print(f"[CloudWatchLogger] Logger level set to: {self.level}")

        # Console handler for local debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
        print("[CloudWatchLogger] Console handler added.")

        try:
            # CloudWatch handler
            print("[CloudWatchLogger] Setting up CloudWatchLogHandler...")
            cloudwatch_handler = CloudWatchLogHandler(
                log_group=self.log_group_name,
                stream_name=self.log_stream_name
            )
            cloudwatch_handler.setLevel(self.level)
            cloudwatch_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(cloudwatch_handler)
            print("[CloudWatchLogger] CloudWatchLogHandler added successfully.")

            # Enable immediate flushing in debug mode
            if self.debug_mode:
                print("[CloudWatchLogger] Debug mode enabled; enabling immediate flush for CloudWatch logs.")
                self._enable_immediate_flush(cloudwatch_handler)
        except Exception as e:
            print(f"[CloudWatchLogger] Error setting up CloudWatchLogHandler: {e}")
            self.logger.error(f"Failed to initialize CloudWatchLogHandler: {e}")

        self.logger.info("CloudWatch logger initialized.")
        return self.logger

    def _enable_immediate_flush(self, handler):
        """Enable immediate flushing of logs for the given handler."""
        original_emit = handler.emit

        def emit_and_flush(record):
            original_emit(record)
            handler.flush()

        handler.emit = emit_and_flush
        print("[CloudWatchLogger] Immediate flush enabled for CloudWatchLogHandler.")

    def _delete_log_stream(self):
        """Delete the log stream if it exists."""
        print(f"[CloudWatchLogger] Attempting to delete log stream: {self.log_stream_name}")
        session = boto3.Session()
        client = session.client("logs", region_name=os.getenv("AWS_REGION", "us-east-1"))
        try:
            client.delete_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name
            )
            print(f"[CloudWatchLogger] Log stream {self.log_stream_name} deleted successfully.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"[CloudWatchLogger] Log stream {self.log_stream_name} does not exist.")
            else:
                print(f"[CloudWatchLogger] Failed to delete log stream: {e}")

# Usage example
def get_logger(log_name="default"):
    # Retrieve the reset_log_stream value from the LOG_RESET environment variable
    reset_log_stream = os.getenv("LOG_RESET", "False").lower() == "true"
    print(f"[CloudWatchLogger] reset_log_stream: {reset_log_stream}")

    # Retrieve the environment name from APP_ENV
    app_env = os.getenv("APP_ENV", "Unknown")
    if app_env == "Unknown":
        print("[CloudWatchLogger] Warning: APP_ENV is not set. Defaulting to 'Unknown'.")
        logging.warning("APP_ENV is not set. Defaulting to 'Unknown'.")

    app_env = "Dev" if app_env.lower() == "development" else "Prod"

    # Construct the log group name
    log_group_name = f"{os.getenv('CLOUDWATCH_GROUP_NAME', 'JensJugs/Api')}/{app_env}"
    log_stream_name = log_name  # Removed the timestamp from the stream name

    print(f"[CloudWatchLogger] Log group: {log_group_name}, Log stream: {log_stream_name}")

    logger = CloudWatchLogger(
        log_group_name=log_group_name,
        log_stream_name=log_stream_name
    )
    return logger.setup_logger(reset_log_stream=reset_log_stream)

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)