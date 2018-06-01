# Nynke Niehof, 2018

import multiprocessing
import unittest
import sys
from os.path import dirname

sys.path.append(dirname(sys.path[0]))
from Experiment.GVSHandler import GVSHandler


class TestHandlerCommunication(unittest.TestCase):

    def setUp(self):
        self.in_queue = multiprocessing.Queue()
        self.out_queue = multiprocessing.Queue()
        self.gvsProcess = multiprocessing.Process(target=GVSHandler,
                                                  args=(self.in_queue,
                                                        self.out_queue))
        self.gvsProcess.start()

    def tearDown(self):
        self.out_queue.put("STOP")

    def test_connection(self):
        self.assertTrue(self.out_queue.get())


if __name__ == "__main__":
    unittest.main()
