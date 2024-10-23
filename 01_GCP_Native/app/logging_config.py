import sys
from loguru import logger

def configure_logger():
    # Remove the default handler first
    logger.remove()

    # Add a file handler (Avoid to load in cloud functions environment!!!)
    # logger.add("./logs/{time:YYYY-MM-DD at HH-mm-ss}.log", format="{level} {message}", level="DEBUG")

    # Add console handler
    logger.add(sys.stdout, format="{level} - Line {line}: {message}", level="DEBUG")

    # Set up a custom exception handler
    def custom_excepthook(exc_type, exc_value, exc_traceback):
        tb = exc_traceback
        while tb and tb.tb_next:  # Traverse to the last frame in the traceback
            tb = tb.tb_next
        line_number = tb.tb_lineno if tb else "unknown"
        logger.critical(f"Error in line {line_number}: {exc_value}")
        sys.exit(1)  # Exit after logging the critical error

    # Override default exception hook
    sys.excepthook = custom_excepthook
