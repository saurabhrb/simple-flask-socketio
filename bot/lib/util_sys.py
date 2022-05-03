import logging
import traceback, threading


class threadFunction:
    def __init__(self, func): # TODO: add func args
        thread = threading.Thread(target=func, args=()) # TODO: pass those args to func
        thread.daemon = True                       # Daemonize thread
        thread.start()                             # Start the execution

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    # handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_exception_traceback(exception):
    tb = ''.join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
    return tb
