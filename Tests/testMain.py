import unittest
import glob
from sys import path
import os

path.append(os.path.dirname(path[0]))
from Experiment.main import SaveData


class TestSaveData(unittest.TestCase):

    def setUp(self):
        self.sj = 99
        self.paradigm = "testParadigm"
        self.condition = "fakeCondition"
        self.root_dir = os.getcwd()
        self.filename_part = "{}_{}_{}_".format(self.sj,
                                                self.paradigm,
                                                self.condition)

    def tearDown(self):
        rubbish_files = glob.glob("{}/Data/*{}/*{}*.txt".format(self.root_dir,
                                                                self.sj,
                                                                self.filename_part))
        for file in rubbish_files:
            os.remove(file)

    def test_file_not_exist(self):
        # find matching files, regardless of leading zeros and time stamp
        files = glob.glob("{}/Data/*{}/*{}*.txt".format(self.root_dir,
                                                        self.sj,
                                                        self.filename_part))
        # list of files matching the name pattern must be empty
        self.assertTrue(not files)

    def test_create_file(self):
        self.datafile = SaveData(self.sj, self.paradigm, self.condition,
                                 root_dir=self.root_dir)
        self.datafile.write_header("testVar1, testVar2")
        files = glob.glob("{}/Data/{}/{}*.txt".format(self.root_dir,
                                                      self.sj,
                                                      self.filename_part))
        self.assertTrue(files)

    def test_create_file_heading_zeros(self):
        self.datafile = SaveData(self.sj, self.paradigm, self.condition,
                                 sj_leading_zeros=3,
                                 root_dir=self.root_dir)
        self.datafile.write_header("testVar1, testVar2")
        files = glob.glob("{}/Data/0{}/0{}*.txt".format(self.root_dir,
                                                        self.sj,
                                                        self.filename_part))
        self.assertTrue(files)


if __name__ == "__main__":
    unittest.main()
