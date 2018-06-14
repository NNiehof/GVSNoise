import multiprocessing
import logging
import time
from sys import path
from os.path import dirname

path.append(dirname(path[0]))
from Experiment.loggingConfig import *


formatter = logging.Formatter("%(asctime)s %(processName)s %(message)s")
default_logging_level = logging.DEBUG
log_file = "test_log.log"

if __name__ == "__main__":
    # set up multiprocessing-aware logging

    # shared queue for logging from subprocesses
    queue_manager = multiprocessing.Manager()
    queue = queue_manager.Queue()

    # set up listener thread that does the logging
    listener = Listener(queue, formatter, default_logging_level, log_file)
    listener.start()

    worker = Worker(queue, formatter, default_logging_level, "worker-log")
    test_logger = worker.logger
    test_logger.log(logging.WARNING, "test message from worker")
    time.sleep(1)
    test_logger.log(None)
    listener.join()


