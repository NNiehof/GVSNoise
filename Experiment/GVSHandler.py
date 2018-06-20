# Nynke Niehof, 2018

from copy import deepcopy
from Experiment.GVS import GVS
from Experiment.genNoiseStim import genStim
from Experiment.loggingConfig import Worker, formatter, default_logging_level


class GVSHandler():
    def __init__(self, param_queue, status_queue, logging_queue):
        # TODO: pass constants as arguments
        PHYSICAL_CHANNEL_NAME = "cDAQ1Mod1/ao0"
        SAMPLING_FREQ = 1e3

        # TODO: REMOVE AFTER DEBUGGING
        logfile = "testGVSHandlerLog.log"

        # I/O queues
        self.param_queue = param_queue
        self.status_queue = status_queue
        self.logging_queue = logging_queue

        # stimulus generation
        self.makeStim = genStim(f_samp=SAMPLING_FREQ)
        self.stimulus = self.makeStim.stim

        # GVS control object
        self.gvs = GVS(logging_queue=logging_queue)
        connected = self.gvs.connect(PHYSICAL_CHANNEL_NAME)
        self.status_queue.put(connected)

        # set up logger
        worker = Worker(logging_queue, formatter, default_logging_level,
                        "GVSHandler")
        logger = worker.logger
        logger.info("GVS handler initialisation complete")

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
                    self.status_queue.put("GVS quit")
                else:
                    self.status_queue.put("quitting GVS failed")
                break

            else:
                if type(data).__name__ == "dict":
                    self._create_stimulus(params=data)

                elif (type(data).__name__ == "bool") & (data is True):
                    self._send_stimulus()

                else:
                    # TODO: log something meaningful about invalid input parameters
                    self.status_queue.put(False)

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
            self.status_queue.put(False)
            return

        if self._check_args(["fade_samples"], params):
            self.makeStim.fade(params["fade_samples"])

        self.stimulus = self.makeStim.stim
        self.status_queue.put(True)

    def _send_stimulus(self):
        """
        Send the stimulus to the GVS channel, check whether all samples
        were successfully written
        """
        samps_written = self.gvs.write_to_channel(self.stimulus)

        if len(self.stimulus) == samps_written:
            self.status_queue.put(True)
        else:
            self.status_queue.put(False)

    def _check_args(self, keylist, check_dict):
        return all(key in check_dict for key in keylist)
