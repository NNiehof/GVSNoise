import multiprocessing
from sys import path
from os.path import dirname

path.append(dirname(path[0]))
from Experiment.loggingConfig import *


def test_worker_process(log_queue, formatter, logging_level, number, logger_name=""):
    worker = Worker(log_queue, formatter, logging_level, logger_name)
    logger = worker.logger
    message = "test message from worker {}".format(number)
    logger.log(logging.INFO, message)


if __name__ == "__main__":
    # set up multiprocessing-aware logging
    log_file = "test_log.log"

    # shared queue for logging from subprocesses
    queue_manager = multiprocessing.Manager()
    log_queue = queue_manager.Queue()

    # set up listener thread that does the logging
    listener = Listener(log_queue, formatter, default_logging_level, log_file)
    listener.start()

    workers = []
    for worker_number in range(4):
        worker = multiprocessing.Process(target=test_worker_process,
                                         args=(log_queue, formatter,
                                               default_logging_level,
                                               worker_number,
                                               "worker-log"))
        worker.daemon = True
        workers.append(worker)
        worker.start()

    for w in workers:
        w.join()

    log_queue.put(None)
    listener.join()
