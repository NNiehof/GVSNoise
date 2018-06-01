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
        self.gvsProcess = GVSHandler(in_queue=self.param_queue,
                                     out_queue=self.status_queue)
        self.gvsProcess.start()
        self.connected = self.status_queue.get()

    def tearDown(self):
        self.param_queue.put("STOP")
        self.gvsProcess.join()
        self.param_queue.close()
        self.status_queue.close()

    def test_connection(self):
        self.assertTrue(self.connected)

    def test_create_stim(self):
        self.param_queue.put({"duration": 5.0, "amp": 1.0})
        self.assertTrue(self.status_queue.get())

    def test_create_stim_with_fade(self):
        self.param_queue.put({"duration": 5.0, "amp": 1.0,
                              "fade_samples": 100.0})
        self.assertTrue(self.status_queue.get())

    def test_incomplete_dict(self):
        self.param_queue.put({"duration": 5.0})
        self.assertFalse(self.status_queue.get())

    def test_wrong_dict(self):
        self.param_queue.put({"something": 5.0, "other": 4.0})
        self.assertFalse(self.status_queue.get())

    def test_wrong_param_type(self):
        self.param_queue.put(5)
        self.assertFalse(self.status_queue.get())

    def test_send_stim(self):
        self.param_queue.put(True)
        self.assertTrue(self.status_queue.get())


if __name__ == "__main__":
    unittest.main()
