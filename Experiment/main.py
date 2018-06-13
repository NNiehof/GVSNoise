import multiprocessing
import logging




if __name__ == "__main__":
    # set up logging from multiple processes

    # shared queue
    queue_manager = multiprocessing.Manager()
    queue = queue_manager.Queue()

    logger = logging.getLogger()
    handler = logging.StreamHandler()

