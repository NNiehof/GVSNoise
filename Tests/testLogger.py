import multiprocessing
import logging
from sys import path
from os.path import dirname

path.append(dirname(path[0]))
from Experiment.loggingConfig import *


formatter = logging.Formatter("%(asctime)s %(message)s")
default_logging_level = logging.DEBUG

if __name__ == "__main__":
    # set up multiprocessing-aware logging

    # shared queue for logging from subprocesses
    queue_manager = multiprocessing.Manager()
    queue = queue_manager.Queue()

    # set up listener thread that does the logging
    listener = threading.Thread(target=Listener,
                                args=(queue, formatter, default_logging_level))
    listener.start()

    worker = Worker(queue, formatter, default_logging_level, "worker-log")
    test_logger = worker.logger
    test_logger.log(logging.DEBUG, "test message from worker")
    listener.join()


