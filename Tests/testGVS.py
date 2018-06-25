# Nynke Niehof, 2018

import numpy as np
import unittest
from sys import path
from os.path import dirname

path.append(dirname(path[0]))
from Experiment.GVS import GVS


class TestMaxVoltage(unittest.TestCase):

    def test_upper_lim(self):
        self.gvs1 = GVS(max_voltage=5.0)
        self.assertAlmostEqual(self.gvs1.max_voltage, 1.0)
        self.gvs1.quit()

    def test_negative_lim(self):
        self.gvs2 = GVS(max_voltage=-40)
        self.assertAlmostEqual(self.gvs2.max_voltage, 1.0)
        self.gvs2.quit()

    def test_change_upper_lim(self):
        self.gvs3 = GVS(max_voltage=2.5)
        self.gvs3.max_voltage = 10
        self.assertAlmostEqual(self.gvs3.max_voltage, 1.0)
        self.gvs3.quit()

    def test_voltage_below_upper_lim(self):
        self.gvs4 = GVS(max_voltage=0.5)
        self.assertAlmostEqual(self.gvs4.max_voltage, 0.5)
        self.gvs4.quit()


def test_signal():
    """
    Generate a signal with an alternating step from 0 V to 1 V and to -1 V.
    Check the generated voltage with an oscilloscope.
    """
    gvs = GVS(max_voltage=3.0)
    connected = gvs.connect("cDAQ1Mod1/ao0")
    if connected:
        samples = np.concatenate((np.zeros(500), np.ones(1000), np.zeros(500)))
        samples = np.concatenate((samples, -samples, samples, -samples))
        gvs.write_to_channel(samples)
    gvs.quit()


if __name__ == "__main__":
    unittest.main()
    test_signal()

