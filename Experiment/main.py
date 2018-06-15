import multiprocessing
import logging
import os
import time
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


class SaveData:

    def __init__(self, sj, paradigm, condition,
                 sj_leading_zeros=0, root_dir=None):
        """

        :param sj: subject identification number
        :param sj_leading_zeros: (optional) add leading zeros to subject
        number until the length of sj_leading_zeros is reached.
        Example:
        with sj_leading_zeros=4, sj_name="2" -> sj_name="0002"
        """
        # set up data folder
        if root_dir is None:
            root_dir = os.path.dirname(os.path.abspath("__file__"))
        datafolder = "{}/Data".format(root_dir)
        if not os.path.isdir(datafolder):
            os.mkdir(datafolder)

        # subject identifier with optional leading zeros
        sj_number = str(sj)
        if sj_leading_zeros > 0:
            while len(sj_number) < sj_leading_zeros:
                sj_number = "0{}".format(sj_number)

        # set up subject folder and data file
        subfolder = "{}/{}".format(datafolder, sj_number)
        if not os.path.isdir(subfolder):
            os.mkdir(subfolder)
        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.datafile = "{}/{}_{}_{}_{}.txt".format(subfolder, sj_number,
                                                paradigm, condition, timestr)

    def write_header(self, header):
        self.write(header)

    def write(self, data_str):
        with open(self.datafile, "a") as f:
            f.write(data_str)

if __name__ == "__main__":
    # set up logging from multiple processes

    # shared queue
    queue_manager = multiprocessing.Manager()
    queue = queue_manager.Queue()

    logger = logging.getLogger()
    handler = logging.StreamHandler()

