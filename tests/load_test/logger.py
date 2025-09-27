import logging
import logging.handlers
import sys
import os
import constants
import queue

LOG_FILE = os.path.join(os.path.dirname(__file__), constants.LOG_FILE)
queueListener = None

def setupLogger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(constants.LOG_LEVEL)

    if not logger.handlers:
        # Console handler
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logging.Formatter(
            constants.LOG_FORMAT
        ))
        # File handler
        fileHandler = logging.FileHandler(LOG_FILE)
        fileHandler.setFormatter(logging.Formatter(
            constants.LOG_FORMAT
        ))
        # Queue handler
        logQueue = queue.Queue(-1)
        queueHandler = logging.handlers.QueueHandler(logQueue)
        queueListener = logging.handlers.QueueListener(
            logQueue,
            consoleHandler,
            fileHandler
        )
        logger.addHandler(queueHandler)
        queueListener.start()

    return logger

def stopLogger():
    if queueListener is not None:
        queueListener.stop()
        logging.shutdown()