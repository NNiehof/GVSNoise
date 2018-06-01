# Nynke Niehof, 2018

import multiprocessing
import unittest
import sys
from os.path import dirname

sys.path.append(dirname(sys.path[0]))
from Experiment.GVSHandler import GVSHandler


class TestHandlerCommunication(unittest.TestCase):

    def setUp(self):
        self.param_queue = multiprocessing.Queue()
        self.status_queue = multiprocessing.Queue()
        self.gvsProcess = multiprocessing.Process(target=GVSHandler,
                                                  args=(self.param_queue,
                                                        self.status_queue))
        self.gvsProcess.start()

    def tearDown(self):
        self.param_queue.put("STOP")
        self.gvsProcess.join()

    def test_connection(self):
        self.assertTrue(self.status_queue.get())

    def test_create_stim(self):
        self.param_queue.put({"duration": 5.0, "amp": 1.0})
        self.assertTrue(self.status_queue.get())


if __name__ == "__main__":
    unittest.main()
