import multiprocessing
import logging
from Experiment.GVSHandler import GVSHandler
from Experiment.loggingConfig import Listener
#TODO: fix the module so that the files don't have to be imported separately

class Experiment():

    def __init__(self):
        # set up listener thread for central logging from all processes
        queue_manager = multiprocessing.Manager()
        self.log_queue = queue_manager.Queue()
        log_listener = Listener(log_queue, formatter, default_logging_level, log_file)
        log_listener.start()

        # establish connection with galvanic stimulator
        self.param_queue = multiprocessing.Queue()
        self.status_queue = multiprocessing.Queue()
        self.gvsProcess = multiprocessing.Process(target=GVSHandler,
                                                  args=(self.param_queue,
                                                        self.status_queue,
                                                        self.log_queue))



if __name__ == "__main__":
    # set up logging from multiple processes

    # shared queue
    queue_manager = multiprocessing.Manager()
    queue = queue_manager.Queue()

    logger = logging.getLogger()
    handler = logging.StreamHandler()

