# Nynke Niehof, 2018

import nidaqmx
from nidaqmx import constants, stream_writers
import time
import logging


class GVS(object):
    """
    Represents a GVS object that communicates with the NIDAQ digital-to-analog
    converter, which sends signals to the Biopac STMISOLA stimulator.
    """
    def __init__(self, max_voltage=1.0, logger=None):
        """
        Create a GVS communication object.

        :param max_voltage: maximum voltage the NIDAQ should generate.
        Note: this translates to a maximum current (with 1 V corresponding to
        1 mA) when the Biopac STMISOLA is in current mode (I). Depending on the
        impedance between the electrodes on the participant's head, the
        generated voltage can vary as V = I * R.

        :param logger: (optional) logging object.
        If undefined, log messages will be sent to the console.
        """
        self.max_voltage = abs(max_voltage)

        # create a task, initialise stream writer
        self.task = nidaqmx.Task()
        self.writer = None

        # set up logger
        if logger is not None:
            self.logger = logger
        else:
            logging.basicConfig(level=logging.DEBUG,
                                format="%(asctime)s %(message)s")
            self.logger = logging.getLogger()

    def connect(self, physical_channel_name):
        """
        Establish connection with NIDAQ apparatus. A virtual output channel
        and data stream writer are created.

        :param physical_channel_name: name of output port on NIDAQ (to see
        available channel names, open NI MAX (software included with driver
        installation) and look under "Devices and Interfaces").
        The name might look something like "cDAQ1Mod1/ao0".
        :return: True if connection was successful, otherwise False.
        """
        try:
            # create virtual output channel
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
            self.logger.error("DAQmx error: {0}".format(err))
            return False

        self.task.start()
        self.logger.info("GVS task started")
        return True

    @property
    def max_voltage(self):
        return self._max_voltage

    @max_voltage.setter
    def max_voltage(self, max_voltage):
        if max_voltage > 1.0:
            self._max_voltage = 1.0
        else:
            self._max_voltage = max_voltage

    def write_to_channel(self, current_profile):
        """
        Send a current profile to the output channel.

        :param current_profile: Numpy array of samples
        :return samps_written: number of samples successfully written
        """
        t_start = time.time()
        self.logger.info("{0} start GVS".format(t_start))

        samps_written = self.writer.write_many_sample(current_profile)
        self.task.wait_until_done(timeout=nidaqmx.constants.WAIT_INFINITELY)

        t_stop = time.time()
        self.logger.info("{0} stop GVS".format(t_stop))
        self.logger.info("GVS duration = {0}".format(t_stop - t_start))

        # write one zero sample to set the baseline back to zero
        # (NIDAQ otherwise maintains the output voltage of the last sample)
        self.writer.write_one_sample(0.0)

        assert isinstance(samps_written, int)
        return samps_written

    def quit(self):
        self.task.stop()
        self.task.close()
        self.logger.info("GVS task closed")
        return True


if __name__ == "__main__":
    gvs = GVS(max_voltage=1.0)
    gvs.quit()
