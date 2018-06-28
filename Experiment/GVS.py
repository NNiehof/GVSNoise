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

    def connect(self, physical_channel_name, **timing_args):
        """
        Establish connection with NIDAQ apparatus. A virtual output channel
        and data stream writer are created.

        :param physical_channel_name: name of output port on NIDAQ (to see
        available channel names, open NI MAX (software included with driver
        installation) and look under "Devices and Interfaces").
        The name might look something like "cDAQ1Mod1/ao0".
        :param sampling_rate: samples per second to generate per channel.
        Default is 10 kHz.
        **timing_args : keyword arguments from
        nidqamx.task.timing.cfg_samp_clk_timing.
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
            # config timing
            self.task.timing.cfg_samp_clk_timing(**timing_args)
            # create output stream writer
            self.writer = stream_writers.AnalogSingleChannelWriter(
                self.task.out_stream, auto_start=True
            )
            logging.info("GVS task and channel created")
        except nidaqmx.errors.DaqError as err:
            self.logger.error("DAQmx error: {0}".format(err))
            return False

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

    def write_to_channel(self, current_profile, reset_to_zero_volts=False):
        """
        Send a current profile to the output channel.

        :param current_profile: Numpy array of samples
        :param reset_to_zero_volts: (bool, optional)
        Changes the final sample to 0 V, to set the excitation level of
        the NIDAQ back to zero. Otherwise, the NIDAQ continues excitation
        at the level of the final sample.
        :return samps_written: number of samples successfully written
        """
        if reset_to_zero_volts:
            # replace the final sample with zero to set the baseline back
            current_profile[-1] = 0.0
            self.logger.info("final current sample set to 0 V")

        t_start = time.time()
        samps_written = self.writer.write_many_sample(current_profile)
        self.task.wait_until_done(timeout=nidaqmx.constants.WAIT_INFINITELY)
        t_stop = time.time()
        self.task.stop()

        self.logger.debug("{0} start GVS".format(t_start))
        self.logger.debug("{0} stop GVS".format(t_stop))
        self.logger.info("GVS duration = {0}".format(t_stop - t_start))

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
