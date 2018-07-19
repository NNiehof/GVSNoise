import multiprocessing
from queue import Empty
import logging
import json
import os
import time
from collections import OrderedDict
from psychopy import visual, core, event
from Experiment.GVSHandler import GVSHandler
from Experiment.loggingConfig import Listener, Worker
from Experiment.stateMachine import StateMachine
from Experiment.blockedStimulus import BlockStim
# TODO: fix the module so that the files don"t have to be imported separately


class Experiment:

    def __init__(self):
        self.sj = 1 # TODO: change to read out
        self.break_after_trials = 120

        # experiment settings and conditions
        self.win = None
        self.frame_duration = 0
        self.paradigm = "GVSNoise"
        self.condition = ""
        self.stimuli = None
        self.triggers = None
        self.logger_main = None
        self.save_data = None
        self.trials = None
        self.break_trials = None
        self.data = dict()
        self.n_trials = 0
        self.make_stim = None

        # root directory
        abs_path = os.path.abspath("__file__")
        self.root_dir = os.path.dirname(os.path.dirname(abs_path))
        self.settings_dir = "{}/Settings".format(self.root_dir)

        # variables for running the experiment states
        self.timer_triggers = {}
        self.statenames = ["start", "init_trial", "pre_probe", "probe",
                           "response"]
        self.durations = dict()
        self.conditions = dict()
        self.start_time = None
        self.trial_count = 0
        self.new_state = None
        self.go_next = False
        self.response_given = False
        self.rod_angle = 0
        self.frame_angle = 0
        self.current = 0

    def setup(self):
        # display and window settings
        self._display_setup()

        # get state durations from json file
        duration_file = "{}/durations.json".format(self.settings_dir)
        with open(duration_file) as json_dur:
            self.durations = json.load(json_dur)

        # set up logging folder, file, and processes
        make_log = SaveData(self.sj, self.paradigm, self.condition,
                            file_type="log", sj_leading_zeros=3,
                            root_dir=self.root_dir)
        log_name = make_log.datafile
        self._logger_setup(log_name)
        main_worker = Worker(self.log_queue, self.log_formatter,
                             self.default_logging_level, "main")
        self.logger_main = main_worker.logger

        # start process which controls the GVS, wait for connection message
        self._gvs_setup()
        self._check_gvs_status("connected")

        # trial list
        conditions_file = "{}/conditions.json".format(self.settings_dir)
        with open(conditions_file) as json_file:
            self.conditions = json.load(json_file)
        self.trials = BlockStim(**self.conditions)
        self.break_trials = range(self.break_after_trials,
                                  len(self.trials.trial_list),
                                  self.break_after_trials)
        self.n_trials = len(self.trials.trial_list)

        # create stimuli
        self.make_stim = Stimuli(self.win, self.settings_dir, self.n_trials)
        self.stimuli, self.triggers = self.make_stim.create()
        self.logger_main.info("stimuli created")

        # data save file
        self.save_data = SaveData(self.sj, self.paradigm, self.condition,
                                  sj_leading_zeros=3, root_dir=self.root_dir)

        # setup state machine that cycles through the experiment
        self.logger_main.info("initiating state machine")
        self._state_machine_setup()
        self.logger_main.info("setup complete")

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
        Establish a connection for parallel processes to log to a single file.

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
        # note: for debugging, comment out the next line. Starting the listener
        # will cause pipe breakage in case of a bug elsewhere in the code,
        # and the console will be flooded with error messages from the
        # listener.
        self.log_listener.start()

    def _gvs_setup(self):
        """
        Establish connection with galvanic stimulator
        """
        self.param_queue = multiprocessing.Queue()
        self.status_queue = multiprocessing.Queue()
        buffer_size = self.durations["gvs"] * 1e3
        self.gvs_process = multiprocessing.Process(target=GVSHandler,
                                                   args=(self.param_queue,
                                                         self.status_queue,
                                                         self.log_queue,
                                                         buffer_size))
        self.gvs_process.start()

    def _state_machine_setup(self):
        """
        Initiate finite state machine to cycle through the experiment stages.
        """
        self.fsm = StateMachine()
        self.fsm.add_state("start", self.start_state)
        self.fsm.add_state("init_trial", self.init_trial_state)
        self.fsm.add_state("pre_probe", self.pre_probe_state)
        self.fsm.add_state("probe", self.probe_state)
        self.fsm.add_state("response", self.response_state)
        self.fsm.add_state("pause", self.pause_state)
        # define end and start state
        self.fsm.add_state("end", self.end_state, end_state=True)
        self.fsm.set_start("start")
        self.fsm.add_logger(self.logger_main)
        self.go_next = False

    def _check_gvs_status(self, key, blocking=True):
        """
        Check the status of *key* on the status queue. Returns a boolean
        for the status. Note: this is a blocking process.
        :param key: str
        :param blocking: bool, set to True to hang until the key parameter
        is found in the queue. Set to False to check the queue once, then
        return.
        :return: bool or None
        """
        while True:
            try:
                status = self.status_queue.get(block=blocking)
                if key in status:
                    return status[key]
            except Empty:
                return None
            if not blocking:
                return None

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
        self.fsm.run()
        self.quit()

    def display_stimuli(self):
        for stim in self.stimuli:
            if self.triggers[stim]:
                self.stimuli[stim].draw()
        self.win.flip()

    def format_data(self):
        formatted_data = "{}, {}, {}, {}, {}, {}\n".format(
            self.data["trialNr"], self.data["trialOnset"],
            self.data["frameAngle"], self.data["rodAngle"],
            self.data["maxCurrent"], self.data["response"])
        return formatted_data

    def check_response(self):
        key_response = event.getKeys(keyList=["left", "right", "space", "escape"])
        state_change = None
        if key_response:
            if "left" in key_response:
                self.data["response"] = False
                state_change = "init_trial"
            elif "right" in key_response:
                self.data["response"] = True
                state_change = "init_trial"
            elif "space" in key_response:
                state_change = "pause"
            elif "escape" in key_response:
                state_change = "end"
        return state_change

    def check_keys(self):
        key_presses = event.getKeys(keyList=["space", "escape"])
        event.clearEvents(eventType="mouse")
        state_change = None
        if key_presses:
            if "space" in key_presses:
                state_change = "pause"
            elif "escape" in key_presses:
                state_change = "end"
        return state_change

    def start_state(self):
        # triggers for controlling the time duration of each state
        for state in self.statenames:
            self.timer_triggers[state] = True
        # wait for space bar press to start experiment
        event.waitKeys(maxWait=float("inf"), keyList=["space"])
        self.new_state = "init_trial"
        self.go_next = True
        return self.new_state, self.go_next

    def init_trial_state(self):
        self.data = dict()
        self.data["trialNr"] = self.trial_count
        self.logger_main.info("trial {}".format(self.trial_count))
        self.response_given = False

        # get stimulus settings for current trial
        trial = self.trials.get_stimulus(self.trial_count)
        self.rod_angle = trial[0]
        self.frame_angle = trial[1]
        self.current = trial[2]
        self.data["trialOnset"] = time.time()
        self.data["rodAngle"] = self.rod_angle
        self.data["frameAngle"] = self.frame_angle
        self.data["maxCurrent"] = self.current
        if self.frame_angle != "noframe":
            self.stimuli["squareFrame"].ori = self.frame_angle
        self.stimuli["rodStim"].ori = self.rod_angle

        # create GVS stimulus in preparation
        block_start = False
        if (self.trial_count % self.conditions["block_size"]) == 0:
            if self.trial_count != 0:
                # wait for GVS of previous block to finish
                while not self._check_gvs_status("stim_sent", blocking=False):
                    self.display_stimuli()
                    # clear event buffer to avoid it filling up and blocking
                    self.check_keys()
            block_start = True
            gvs_duration = self.durations["gvs"]
            fade_samples = self.durations["fade"] * 1000
            self.param_queue.put({"duration": gvs_duration, "amp": self.current,
                                  "fade_samples": fade_samples})
            # check whether the gvs profile was successfully created
            if self._check_gvs_status("stim_created"):
                self.logger_main.info("gvs current profile created")
            else:
                self.logger_main.warning("WARNING: current profile not created")

        self.display_stimuli()

        # send the GVS signal to the stimulator
        if block_start:
            self.param_queue.put(True)
            # hang during the fade-in
            gvs_start = time.time()
            while (time.time() - gvs_start) < self.durations["fade"]:
                self.display_stimuli()

        # reset state timer triggers
        for state in self.statenames:
            self.timer_triggers[state] = True
        self.new_state = "pre_probe"
        self.go_next = True
        return self.new_state, self.go_next

    def pre_probe_state(self):
        # start the timer for the current state (once per trial)
        if self.timer_triggers["pre_probe"]:
            self.pre_probe_timer = time.time()
            self.timer_triggers["pre_probe"] = False
        # display stimulus
        if self.frame_angle != "noframe":
            self.triggers["squareFrame"] = True
        self.display_stimuli()

        # go to next state based on key presses or timer
        self.new_state = self.check_keys()
        if self.new_state == "pause":
            self.go_next = False
        elif self.new_state == "end":
            self.go_next = True
        else:
            # if no key was pressed, go to probe state after timer runs out
            self.new_state = "probe"
            if (time.time() - self.pre_probe_timer) > self.durations["pre_probe"]:
                self.go_next = True
            else:
                self.go_next = False
        return self.new_state, self.go_next

    def probe_state(self):
        if self.timer_triggers["probe"]:
            self.probe_timer = time.time()
            self.timer_triggers["probe"] = False
        if self.data["frameAngle"] != "noframe":
            self.triggers["squareFrame"] = True
        self.triggers["rodStim"] = True
        self.display_stimuli()

        self.new_state = self.check_keys()
        if self.new_state == "pause":
            self.go_next = False
        elif self.new_state == "end":
            self.go_next = True
        else:
            self.new_state = "response"
            if (time.time() - self.probe_timer) > self.durations["probe"]:
                self.go_next = True
            else:
                self.go_next = False
        return self.new_state, self.go_next

    def response_state(self):
        if self.timer_triggers["response"]:
            self.response_timer = time.time()
            self.timer_triggers["response"] = False
        if self.data["frameAngle"] != "noframe":
            self.triggers["squareFrame"] = True
        self.triggers["rodStim"] = False
        self.display_stimuli()

        time_up = (time.time() - self.response_timer)\
            > self.durations["response"]

        # check whether response is given
        if time_up and self.response_given:
            self.trial_count += 1
            if self.trial_count in self.break_trials:
                self.new_state = "pause"
                self.go_next = True
            else:
                self.new_state = "init_trial"
                self.go_next = True
        elif time_up:
            # TODO: save missed trials for later rerunning
            self.trial_count += 1
            self.triggers["squareFrame"] = False
            if self.trial_count in self.break_trials:
                self.new_state = "pause"
                self.go_next = True
            else:
                self.new_state = "init_trial"
                self.go_next = True
        else:
            self.new_state = self.check_response()
            if self.new_state == "init_trial":
                self.triggers["squareFrame"] = False
                self.response_given = True
                formatted_data = self.format_data()
                self.save_data.write(formatted_data)
            elif self.new_state == "pause":
                # manual pausing is disabled
                self.go_next = False
            elif self.new_state == "end":
                self.go_next = True
            else:
                # new state may not be None
                self.new_state = "init_trial"
                self.go_next = False
        if not (self.trial_count < self.n_trials):
            # TODO: run missed trials
            self.new_state = "end"
        return self.new_state, self.go_next

    def pause_state(self):
        # make all stimuli invisible
        for stim in self.triggers:
            self.triggers[stim] = False
        self.make_stim.draw_pause_screen(self.trial_count)
        event.waitKeys(maxWait=float("inf"), keyList=["space"])
        self.new_state = "init_trial"
        self.go_next = True
        return self.new_state, self.go_next

    def end_state(self):
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

    def __init__(self, window, settings_dir, n_trials=0):
        """
        Create visual stimuli with PsychoPy.

        :param window: psychopy window instance
        :param settings_dir: directory where the stimulus settings are saved
        (stimuli.json)
        :param n_trials: (optional) number of trials for on pause screen
        """
        self.stimuli = OrderedDict()
        self.triggers = {}

        self.settings_dir = settings_dir
        self.num_trials = n_trials
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

    def draw_pause_screen(self, current_trial):
        win_width, win_height = self.win.size
        pause_screen = visual.Rect(win=self.win, width=win_width,
                                   height=win_height, lineColor=(0, 0, 0),
                                   fillColor=(0, 0, 0))
        pause_str = "PAUSE  trial {}/{} Press space to continue".format(
            current_trial, self.num_trials)
        pause_text = visual.TextStim(win=self.win, text=pause_str,
                                     pos=(0.0, 0.0), color=(-1, -1, 0.6),
                                     units="pix", height=40)
        pause_screen.draw()
        pause_text.draw()
        self.win.flip()


if __name__ == "__main__":
    exp = Experiment()
    exp.setup()
    exp.run()
