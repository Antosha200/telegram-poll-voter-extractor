import logging
import os
from pathlib import Path
from datetime import datetime
import inspect

_logger_initialized = False

def setup_logger():
    global _logger_initialized

    logs_dir = Path(__file__).resolve().parent.parent.parent / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger("app_logger")

    if not _logger_initialized:
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        _logger_initialized = True

    return logger

def log(level, message, *args, **kwargs):
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    lineno = frame.f_lineno

    full_message = f"[{filename}:{lineno}] {message}"
    logger.log(level, full_message, *args, **kwargs)

logger = setup_logger()