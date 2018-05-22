# Nynke Niehof, 2018

import sys
import nidaqmx


class GVS:
    def __init__(self, max_voltage=3.0):

        # limit to 3 Volts
        if max_voltage > 3.0:
            self.max_voltage = 3.0
        else:
            self.max_voltage = max_voltage

        # create a task and virtual output channel
        try:
            task = nidaqmx.Task()
            physical_channel_name = "cDAQ1Mod1/ao0"
            task.ao_channels.add_ao_voltage_chan(
                physical_channel_name,
                name_to_assign_to_channel="GVSoutput",
                min_val=-self.max_voltage,
                max_val=self.max_voltage,
                units=nidaqmx.constants.VoltageUnits.VOLTS)
            print "GVS task and channel created"
        except nidaqmx.errors.DaqError as err:
            print "DAQmx error: %s" % err
            sys.exit(1)

        # start the task
        task.start()
        print "GVS task started"
