# Nynke Niehof, 2018

import multiprocessing
import unittest
import sys
from os.path import dirname

sys.path.append(dirname(sys.path[0]))
from Experiment.GVSHandler import GVSHandler


class TestHandlerCommunication(unittest.TestCase):

    def setUp(self):
        self.module_as_main(True)
        self.in_queue = multiprocessing.Queue()
        self.out_queue = multiprocessing.Queue()
        self.gvsProcess = multiprocessing.Process(target=GVSHandler,
                                                  args=(self.in_queue,
                                                        self.out_queue))

    def tearDown(self):
        self.out_queue.put("STOP")
        self.module_as_main(False)
        self.in_queue.dispose()
        self.out_queue.dispose()
        self.gvsProcess.dispose()

    def test_connection(self):
        self.assertTrue(self.out_queue.get())

    def module_as_main(self, change_to_module):
        """
        Workaround for using *unittest* with code that uses multiprocessing in
        Windows. Workaround copied from the following gist:
        https://gist.github.com/Kerrigan29a/4f459c901a21951ad1bd

        :param change_to_module: (bool) set to True to point __main__ to the
        module to be executed, that uses multiprocessing. Set to False to
        change it back to the original __main__.
        """
        if change_to_module:
            self.old_main = sys.modules["__main__"]
            self.old_main_file = sys.modules["__main__"].__file__
            sys.modules["__main__"] = sys.modules["Experiment.GVSHandler"]
            sys.modules["__main__"].__file__ =\
                sys.modules["Experiment.GVSHandler"].__file__

        else:
            sys.modules["__main__"] = self.old_main
            sys.modules["__main__"].__file__ = self.old_main_file

if __name__ == "__main__":
    unittest.main()
