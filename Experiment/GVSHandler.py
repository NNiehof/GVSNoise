# Nynke Niehof, 2018

import multiprocessing
from GVS import GVS
from genNoiseStim import genStim


class GVSHandler(multiprocessing.Process):
    def __init__(self, in_queue=None, out_queue=None):
        # init superclass
        multiprocessing.Process.__init__(self)

        # constants
        PHYSICAL_CHANNEL_NAME = "cDAQ1Mod1/ao0"
        SAMPLING_FREQ = 1e4

        # REMOVE AFTER DEBUGGING
        logfile = "testGVSHandlerLog.log"

        # I/O queues
        self.in_queue = in_queue
        self.out_queue = out_queue

        # stimulus generation
        self.makeStim = genStim(f_samp=SAMPLING_FREQ)
        self.stimulus = self.makeStim.stim

        # GVS control object
        self.gvs = GVS(logfile=logfile)
        connected = self.gvs.connect(PHYSICAL_CHANNEL_NAME)
        self.out_queue.put(connected)

    def run(self):
        """
        Extends multiprocessing.Process.run and is called when the process's
        start() or run() method is called.

        Event loop that listens for queue input. Input of type *dict* is used
        for stimulus creation, input of type *int* is used to trigger onset of
        GVS stimulation. Input "STOP" to exit the method.
        """
        while True:
            data = self.in_queue.get()
            if data == "STOP":
                self.gvs.quit()
                # log something
                break

            else:
                if type(data).__name__ == "dict":
                    self._create_stimulus(options=data)

                elif type(data).__name__ == "bool":
                    self._send_stimulus()


    def _create_stimulus(self, options=dict):
        """
        Create stimulus array with parameters defined in *options*
        :param options: (dict)
        """
        if self._check_args(["duration", "amp"], options):
            self.makeStim.noise(options["duration"], options["amp"], **options)
        else:
            self.out_queue.put(False)

        if self._check_args(["fade_samples"], options):
            self.makeStim.fade(options["fade_samples"])

        self.stimulus = self.makeStim.stim
        self.out_queue.put(True)

    def _send_stimulus(self):
        """
        Send the stimulus to the GVS channel, check whether all samples
        were successfully written
        """
        samps_written = self.gvs.write_to_channel(self.stimulus)

        if len(self.stimulus) == samps_written:
            self.out_queue.put(True)
        else:
            self.out_queue.put(False)

    def _check_args(self, keylist, check_dict):
        return all(key in check_dict for key in keylist)
