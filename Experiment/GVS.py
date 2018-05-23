# Nynke Niehof, 2018

import sys
import nidaqmx
from nidaqmx import constants, stream_writers
import time
import logging


class GVS(object):
    def __init__(self, max_voltage=3.0, logfile=None):

        self.max_voltage = abs(max_voltage)

        # set up log file
        if not logfile:
            print "Warning: no logfile specified in call to GVS class. " \
                  "All messages will be displayed in console instead."
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(message)s')
        else:
            logging.basicConfig(filename=logfile, level=logging.DEBUG,
                                format='%(asctime)s %(message)s')

        try:
            # create a task and virtual output channel
            self.task = nidaqmx.Task()
            physical_channel_name = "cDAQ1Mod1/ao0"
            self.task.ao_channels.add_ao_voltage_chan(
                physical_channel_name,
                name_to_assign_to_channel="GVSoutput",
                min_val=-self.max_voltage,
                max_val=self.max_voltage,
                units=constants.VoltageUnits.VOLTS
            )
            # create output stream writer
            self.writer = stream_writers.AnalogSingleChannelWriter(
                self.task.out_stream, auto_start=True
            )
            logging.info("GVS task and channel created")
        except nidaqmx.errors.DaqError as err:
            logging.ERROR("DAQmx error: {0}".format(err))
            sys.exit(1)

        self.task.start()
        logging.info("GVS task started")

    @property
    def max_voltage(self):
        return self._max_voltage

    @max_voltage.setter
    def max_voltage(self, max_voltage):
        if max_voltage > 3.0:
            self._max_voltage = 3.0
        else:
            self._max_voltage = max_voltage

    def write_to_channel(self, current_profile):
        """
        Send a current profile to the output channel.

        :param current_profile: Numpy array of samples
        :return:
        """
        t_start = time.time()
        logging.info("{0} start GVS".format(t_start))

        self.writer.write_many_sample(current_profile)
        self.task.wait_until_done(timeout=30.0)

        t_stop = time.time()
        logging.info("{0} stop GVS".format(t_stop))
        logging.info("GVS duration = {0}".format(t_stop - t_start))

    def quit(self):
        self.task.stop()
        self.task.close()
        logging.info("GVS task closed")


if __name__ == "__main__":
    gvs = GVS(max_voltage=3.0, logfile="GVSlog.log")
    gvs.quit()
