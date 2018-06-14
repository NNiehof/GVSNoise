import logging
import logging.handlers
import threading
import sys
import traceback


class Listener(threading.Thread):

    def __init__(self, queue, formatter, default_logging_level, log_file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.formatter = formatter
        self.default_level = default_logging_level
        self.root_logger = None
        self.log_file = log_file

    def _listener_config(self):
        self.root_logger = logging.getLogger()
        # logging to file
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(self.formatter)
        self.root_logger.addHandler(file_handler)
        # logging to console
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        self.root_logger.addHandler(handler)
        self.root_logger.setLevel(self.default_level)

    def run(self):
        self._listener_config()

        while True:
            try:
                record = self.queue.get()
                if record is None:
                    break
                logger = logging.getLogger(record.name)
                logger.callHandlers(record)
            except Exception:
                print("Error in logging Listener: ", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)


class Worker:

    def __init__(self, queue, formatter, logging_level, logger_name):
        self.queue = queue
        self.logger = logging.getLogger(logger_name)
        handler = logging.handlers.QueueHandler(self.queue)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging_level)
