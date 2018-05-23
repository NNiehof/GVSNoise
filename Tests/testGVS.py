# Nynke Niehof, 2018

import unittest
from sys import path
from os.path import dirname

path.append(dirname(path[0]))
from Experiment.GVS import GVS


class test_max_voltage(unittest.TestCase):

    def test_upper_lim(self):
        self.gvs1 = GVS(max_voltage=5.0, logfile="testGVSlog.log")
        self.assertAlmostEqual(self.gvs1.max_voltage, 3.0)
        self.gvs1.quit()

    def test_negative_lim(self):
        self.gvs2 = GVS(max_voltage=-40, logfile="testGVSlog.log")
        self.assertAlmostEqual(self.gvs2.max_voltage, 3.0)
        self.gvs2.quit()

    def test_change_upper_lim(self):
        self.gvs3 = GVS(max_voltage=2.5, logfile="testGVSlog.log")
        self.gvs3.max_voltage = 10
        self.assertAlmostEqual(self.gvs3.max_voltage, 3.0)
        self.gvs3.quit()

    def test_voltage_below_upper_lim(self):
        self.gvs4 = GVS(max_voltage=2.5, logfile="testGVSlog.log")
        self.assertAlmostEqual(self.gvs4.max_voltage, 2.5)
        self.gvs4.quit()


if __name__ == "__main__":
    unittest.main()



