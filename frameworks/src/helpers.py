import logging
from termcolor import colored

# Custom log level for "success" messages (between INFO and WARNING)
SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")

# Custom formatter with color support
class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors based on log level."""
    
    COLORS = {
        logging.DEBUG: "blue",
        logging.INFO: "blue",
        SUCCESS: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "red",
    }
    
    def format(self, record):
        message = super().format(record)
        color = self.COLORS.get(record.levelno, "white")
        return colored(message, color)


def setup_logger(verbose: int = 1) -> logging.Logger:
    """
    Set up and configure the stega logger based on verbosity level.
    
    Args:
        verbose (int): Verbose level (0-4, higher = more output)
            0: Only errors and critical success/info messages
            1: Normal operation messages (default)
            2: Detailed operation messages
            3: Debug messages
            4+: Trace-level messages
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("stega")
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Map verbose levels to logging levels
    # Higher verbose = lower log level threshold (more output)
    level_map = {
        0: logging.ERROR,      # Only errors
        1: SUCCESS,            # Success and above
        2: logging.INFO,       # Info and above
        3: logging.DEBUG,      # Debug and above
        4: logging.DEBUG,      # Everything (DEBUG is lowest)
    }
    
    log_level = level_map.get(verbose, logging.DEBUG if verbose > 4 else logging.ERROR)
    logger.setLevel(log_level)
    
    # Create console handler with colored formatter
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)  # Handler accepts all, logger filters
    formatter = ColoredFormatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def get_logger() -> logging.Logger:
    """Get the stega logger instance."""
    return logging.getLogger("stega")


# Convenience methods for the logger
def log_info(msg: str):
    """Log an info message."""
    get_logger().info(msg)


def log_success(msg: str):
    """Log a success message."""
    get_logger().log(SUCCESS, msg)


def log_warning(msg: str):
    """Log a warning message."""
    get_logger().warning(msg)


def log_error(msg: str):
    """Log an error message."""
    get_logger().error(msg)


def log_debug(msg: str):
    """Log a debug message."""
    get_logger().debug(msg)