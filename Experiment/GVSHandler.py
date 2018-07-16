# Nynke Niehof, 2018

from copy import deepcopy
from Experiment.GVS import GVS
from Experiment.genNoiseStim import GenStim
from Experiment.loggingConfig import Worker, formatter, default_logging_level


class GVSHandler():
    def __init__(self, param_queue, status_queue, logging_queue, buffer_size):
        PHYSICAL_CHANNEL_NAME = "cDAQ1Mod1/ao0"
        SAMPLING_FREQ = 1e3

        # I/O queues
        self.param_queue = param_queue
        self.status_queue = status_queue
        self.logging_queue = logging_queue

        # stimulus generation
        self.makeStim = GenStim(f_samp=SAMPLING_FREQ)
        self.stimulus = self.makeStim.stim

        # set up logger
        worker = Worker(logging_queue, formatter, default_logging_level,
                        "GVSHandler")
        self.logger = worker.logger
        # second logger to pass to GVS object
        subworker = Worker(logging_queue, formatter, default_logging_level,
                           "GVS")
        self.sublogger = subworker.logger

        # GVS control object
        self.gvs = GVS(logger=self.sublogger)
        self.buffer_size = int(buffer_size)
        timing = {"rate": SAMPLING_FREQ, "samps_per_chan": self.buffer_size}
        connected = self.gvs.connect(PHYSICAL_CHANNEL_NAME, **timing)
        if connected:
            self.logger.info("NIDAQ connection established")
            self.status_queue.put({"connected": True})
        else:
            self.logger.info("NIDAQ connection failed")
            self.status_queue.put({"connected": False})

        # GVSHandler can't be a subclass of multiprocessing.Process, as the
        # GVS object contains ctypes pointers and can't be pickled.
        # GVSHandler's methods can't be accessed from the parent process.
        # As a workaround, the event loop is started by calling the run method
        # here at the end of the initialisation.
        self.run()

    def run(self):
        """
        Event loop that listens for queue input. Input of type *dict* is used
        for stimulus creation, input of type *int* is used to trigger onset of
        GVS stimulation. Input "STOP" to exit the method.
        This event loop is automatically started after a GVSHandler object
        is initialised.
        """
        while True:
            data = self.param_queue.get()
            if data == "STOP":
                quitted = self.gvs.quit()
                if quitted:
                    self.status_queue.put({"quit": True})
                else:
                    self.status_queue.put({"quit": False})
                break

            else:
                if type(data).__name__ == "dict":
                    self._create_stimulus(params=data)

                elif (type(data).__name__ == "bool") & (data is True):
                    self._send_stimulus()

                else:
                    self.logger.error("Incorrect input to GVSHandler parameter"
                                      " queue. Input must be a dict with "
                                      "parameters specified in GVS.py, a "
                                      "boolean, or a string STOP to quit.")
                    self.status_queue.put({"stim_created": False})

    def _create_stimulus(self, params=dict):
        """
        Create stimulus array with parameters defined in *params*
        :param params: (dict)
        """
        if self._check_args(["duration", "amp"], params):
            options = deepcopy(params)
            del options["duration"]
            del options["amp"]
            if "fade_samples" in options:
                del options["fade_samples"]
            self.makeStim.noise(params["duration"], params["amp"], **options)
        else:
            self.status_queue.put({"stim_created": False})
            return

        if self._check_args(["fade_samples"], params):
            self.makeStim.fade(params["fade_samples"])

        self.stimulus = self.makeStim.stim
        self.status_queue.put({"stim_created": True})

    def _send_stimulus(self):
        """
        Send the stimulus to the GVS channel, check whether all samples
        were successfully written
        """
        n_samples = None
        samps_written = 0
        try:
            samps_written = self.gvs.write_to_channel(self.stimulus,
                                                      reset_to_zero_volts=True)
            n_samples = len(self.stimulus)
            # delete stimulus after sending, so that it can only be sent once
            self.stimulus = None
        except AttributeError as err:
            self.logger.error("Error: tried to send invalid stimulus to NIDAQ."
                              "\nNote that a stimulus instance can only be"
                              " sent once.\nAttributeError: {}".format(err))
        self.logger.info("GVS: {} samples written".format(samps_written))

        if n_samples == samps_written:
            self.status_queue.put({"stim_sent": True})
        else:
            self.status_queue.put({"stim_sent": False})

    def _check_args(self, keylist, check_dict):
        return all(key in check_dict for key in keylist)
