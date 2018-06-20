import multiprocessing
import logging
import json
import os
import time
from collections import OrderedDict
from psychopy import visual, core, event
from Experiment.GVSHandler import GVSHandler
from Experiment.loggingConfig import Listener, Worker
from Experiment.stateMachine import StateMachine
#TODO: fix the module so that the files don't have to be imported separately


class Experiment:

    def __init__(self):
        self.sj = 1 # TODO: change to read out
        self.win = None
        self.frame_duration = 0
        self.paradigm = "GVSNoise"
        self.condition = ""
        self.stimuli = None
        self.triggers = None
        self.logger_main = None
        self.save_data = None

        # root directory
        abs_path = os.path.abspath("__file__")
        self.root_dir = os.path.dirname(os.path.dirname(abs_path))
        self.settings_dir = "{}/Settings".format(self.root_dir)

    def setup(self):
        # display and window settings
        self._display_setup()

        # set up logging folder, file, and processes
        make_log = SaveData(self.sj, self.paradigm, self.condition,
                            file_type="log", sj_leading_zeros=3,
                            root_dir=self.root_dir)
        log_name = make_log.datafile
        self._logger_setup(log_name)
        main_worker = Worker(self.log_queue, self.log_formatter,
                                  self.default_logging_level, "main")
        self.logger_main = main_worker.logger

        # start process that controls the GVS, wait for connection message
        self._gvs_setup()
        self._check_gvs_status("connected")

        # create stimuli
        stim = Stimuli(self.win, self.settings_dir)
        self.stimuli, self.triggers = stim.create()

        # data save file
        self.save_data = SaveData(self.sj, self.paradigm, self.condition,
                                  sj_leading_zeros=3, root_dir=self.root_dir)

    def _display_setup(self):
        """
        Window and display settings
        """
        display_file = "{}/display.json".format(self.settings_dir)
        with open(display_file) as json_file:
            win_settings = json.load(json_file)
        self.win = visual.Window(**win_settings)
        framerate = self.win.fps()
        self.frame_duration = 1.0/framerate
        self.mouse = event.Mouse(visible=False, win=self.win)

    def _logger_setup(self, log_file):
        """
        Establish a connection for parallel processes to log to s single file.

        :param log_file: str
        """
        # settings
        self.log_formatter = logging.Formatter("%(asctime)s %(processName)s %(thread)d %(message)s")
        self.default_logging_level = logging.DEBUG

        # set up listener thread for central logging from all processes
        queue_manager = multiprocessing.Manager()
        self.log_queue = queue_manager.Queue()
        self.log_listener = Listener(self.log_queue, self.log_formatter,
                                     self.default_logging_level, log_file)
        self.log_listener.start()

    def _gvs_setup(self):
        """
        Establish connection with galvanic stimulator
        """
        self.param_queue = multiprocessing.Queue()
        self.status_queue = multiprocessing.Queue()
        self.gvs_process = multiprocessing.Process(target=GVSHandler,
                                                   args=(self.param_queue,
                                                         self.status_queue,
                                                         self.log_queue))
        self.gvs_process.start()

    def _state_machine_setup(self):
        """
        Initiate finite state machine to cycle through the experiment stages.
        """
        self.fsm = StateMachine()
        self.fsm.add_state("start", self.start_state)
        self.fsm.add_state("init_trial", self.init_trial_state)
        self.fsm.add_state("iti", self.iti_state)
        self.fsm.add_state("pre_probe", self.pre_probe_state)
        self.fsm.add_state("probe", self.probe_state)
        self.fsm.add_state("response", self.response_state)
        # define end and start state
        self.fsm.add_state("end", self.end_state, end_state=True)
        self.fsm.set_start("start")
        self.go_next = False


    def _check_gvs_status(self, key):
        """
        Check the status of *key* on the status queue. Returns a boolean
        for the status. Note: this is a blocking process.
        :param key: str
        :return: bool
        """
        while True:
            status = self.status_queue.get()
            if key in status:
                return status[key]

    def quit(self):
        # send the stop signal to the GVS handler
        self.logger_main.info("quitting")
        self.param_queue.put("STOP")
        # wait for the GVS process to quit
        while True:
            if self._check_gvs_status("quit"):
                break
        # stop GVS and logging processes
        self.gvs_process.join()
        self.log_queue.put(None)
        self.log_listener.join()

        # close psychopy window and the program
        self.win.close()
        core.quit()

    def run(self):
        # TODO: implement experimental states
        frame = 0
        while True:
            for stim in self.stimuli:
                    if self.triggers[stim]:
                        self.stimuli[stim].draw()
            self.win.flip()
            frame += 1
            if frame > 180:
                break
        time.sleep(8)
        self.quit()



class SaveData:

    def __init__(self, sj, paradigm, condition, file_type="data",
                 sj_leading_zeros=0, root_dir=None):
        """
        Create a data folder and .txt or .log file, write data to file.

        :param sj: int, subject identification number
        :param paradigm: string
        :param condition: string
        :param file_type: type of file to create, either "data" (default)
        or "log" to make a log file.
        :param sj_leading_zeros: int (optional), add leading zeros to subject
        number until the length of sj_leading_zeros is reached.
        Example:
        with sj_leading_zeros=4, sj_name="2" -> sj_name="0002"
        :param root_dir: (optional) directory to place the Data folder in
        """
        # set up data folder
        if root_dir is None:
            abs_path = os.path.abspath("__file__")
            root_dir = os.path.dirname(os.path.dirname(abs_path))
        # set up subdirectory "Data" or "Log"
        assert(file_type in ["data", "log"])
        datafolder = "{}/{}".format(root_dir, file_type.capitalize())
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
        if file_type == "data":
            self.datafile = "{}/{}_{}_{}_{}.txt".format(subfolder, sj_number,
                                                        paradigm, condition,
                                                        timestr)
        else:
            self.datafile = "{}/{}_{}_{}_{}.log".format(subfolder, sj_number,
                                                        paradigm, condition,
                                                        timestr)

    def write_header(self, header):
        self.write(header)

    def write(self, data_str):
        with open(self.datafile, "a") as f:
            f.write(data_str)


class Stimuli:

    def __init__(self, window, settings_dir):
        """
        Create visual stimuli with PsychoPy.

        :param window: psychopy window instance
        """
        self.stimuli = OrderedDict()
        self.triggers = {}

        self.settings_dir = settings_dir
        self.win = window

    def create(self):
        # read stimulus settings from json file
        stim_file = "{}/stimuli.json".format(self.settings_dir)
        with open(stim_file) as json_stim:
            stim_config = json.load(json_stim)

        # cycle through stimuli
        for key, value in stim_config.items():
            # get the correct stimulus class to call from the visual module
            stim_class = getattr(visual, value.get("stimType"))
            stim_settings = value.get("settings")
            self.stimuli[key] = stim_class(self.win, **stim_settings)
            # create stimulus trigger
            self.triggers[key] = False

        return self.stimuli, self.triggers


if __name__ == "__main__":
    exp = Experiment()
    exp.setup()
    for trig in exp.triggers:
        exp.triggers[trig] = True
    exp.run()
