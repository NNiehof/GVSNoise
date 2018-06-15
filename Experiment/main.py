import multiprocessing
import logging
import os
import time
from collections import OrderedDict
from psychopy import visual, core, event
from Experiment.GVSHandler import GVSHandler
from Experiment.loggingConfig import Listener
#TODO: fix the module so that the files don't have to be imported separately


class Experiment:

    def __init__(self):
        self.win = None
        self.frame_duration = 0
        self.mouse = None

    def _display_setup(self):
        """
        Window and display settings
        """
        #TODO: read settings in from file
        self.win = visual.Window(winType='pygame', units='pix', fullscr=False)
        framerate = self.win.fps()
        self.frame_duration = 1.0/framerate
        self.mouse = event.Mouse(visible=False, win=self.win)

    def logger_setup(self):
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
        Create a data folder and .txt file, write data to file.

        :param sj: int, subject identification number
        :param paradigm: string
        :param condition: string
        :param sj_leading_zeros: int (optional), add leading zeros to subject
        number until the length of sj_leading_zeros is reached.
        Example:
        with sj_leading_zeros=4, sj_name="2" -> sj_name="0002"
        :param root_dir: (optional) directory to place the Data folder in
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


class Stimuli:

    def __init__(self, window):
        """
        Create visual stimuli with PsychoPy.

        :param window: psychopy window instance
        """
        self.stimuli = OrderedDict()
        self.triggers = {}
        self.win = window

    def create(self):
        #TODO: read stimulus params from file instead of hard-coding

        self.stimuli["rodStim"] = visual.Line(win=self.win, start=(0, -100),
                                              end=(0, 100), lineWidth=5,
                                              lineColor=(-0.8, -0.8, -0.8))

        self.stimuli['squareFrame'] = visual.Rect(win=self.win, width=300.0,
                                                  height=300.0, pos=(0, 0),
                                                  lineWidth=5,
                                                  lineColor=(-0.8, -0.8, -0.8),
                                                  fillColor=None, ori=0.0,
                                                  units="pix")

        # stimulus triggers
        for stim in self.stimuli:
            self.triggers[stim] = False


if __name__ == "__main__":
    # set up logging from multiple processes

    # shared queue
    queue_manager = multiprocessing.Manager()
    queue = queue_manager.Queue()

    logger = logging.getLogger()
    handler = logging.StreamHandler()

