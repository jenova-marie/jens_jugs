import logging
from watchtower import CloudWatchLogHandler
from datetime import datetime
import os

class CloudWatchLogger:
    def __init__(self, log_group_name, log_stream_name, level=logging.INFO):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.level = level
        self.logger = None

    def setup_logger(self):
        if self.logger:
            print("[CloudWatchLogger] Logger already initialized.")
            return self.logger

        print(f"[CloudWatchLogger] Initializing logger for log group: {self.log_group_name}, log stream: {self.log_stream_name}")

        # Create a logger
        self.logger = logging.getLogger(self.log_stream_name)
        self.logger.setLevel(self.level)

        # Console handler for local debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
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
        except Exception as e:
            print(f"[CloudWatchLogger] Error setting up CloudWatchLogHandler: {e}")
            self.logger.error(f"Failed to initialize CloudWatchLogHandler: {e}")

        self.logger.info("CloudWatch logger initialized.")
        return self.logger

# Usage example
def get_logger(log_name="default"):
    # Retrieve the environment name from APP_ENV
    app_env = os.getenv("APP_ENV", "Unknown")
    if app_env == "Unknown":
        print("[CloudWatchLogger] Warning: APP_ENV is not set. Defaulting to 'Unknown'.")
        logging.warning("APP_ENV is not set. Defaulting to 'Unknown'.")

    app_env = "Dev" if app_env.lower() == "development" else "Prod"

    # Construct the log group name
    log_group_name = f"{os.getenv('CLOUDWATCH_GROUP_NAME', 'JensJugs/Api')}/{app_env}"
    log_stream_name = f"{log_name}-{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}"

    print(f"[CloudWatchLogger] Log group: {log_group_name}, Log stream: {log_stream_name}")

    logger = CloudWatchLogger(
        log_group_name=log_group_name,
        log_stream_name=log_stream_name
    )
    return logger.setup_logger()