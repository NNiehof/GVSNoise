from random import shuffle
from Experiment.getTrial import GetNextTrial
from sys import version_info
import warnings
import numpy as np


class RandStim(GetNextTrial):

    def __init__(self, stimulus_range, repeats, **conditions):
        """
        Object that creates a randomised list of trials, out of a range of
        stimulus values and conditions.
        :param stimulus_range: range
        :param repeats: number of repeats per combination
        :param conditions: list
        """

        GetNextTrial.__init__(self, stimulus_range, repeats)
        # trial list with all combinations of stimulus values and conditions
        self.trial_list = self.probes
        if version_info[0] < 3 or version_info[1] < 6:
            warnings.warn("Order of kwargs is not preserved in Python "
                          "< 3.6. Conditions may end up in the trial list "
                          "in an unspecified order.", RuntimeWarning)
        n_cond = sum([len(levels) for cond, levels in conditions.items()])
        self.trial_list = np.repeat(self.trial_list, n_cond, axis=0)
        self.trial_list = self.trial_list[..., np.newaxis]
        levels_mat = np.zeros((len(self.trial_list), len(conditions)))
        i_cond = 0
        for cond, levels in conditions.items():

            reps = int(len(self.trial_list) / len(levels))
            c = np.(np.array(levels), reps, axis=0)
            levels_mat[:, i_cond] = c
            i_cond += 1

        print(np.shape(self.trial_list))
        print(np.shape(levels_mat))
        self.trial_list = np.column_stack((self.trial_list, levels_mat))
    # shuffle(self.trial_list)

    def get_stimulus(self, trial_nr):
        """
        Return stimulus and conditions for next trial
        :return trial: list with [stimulus_value, conditions]
        """
        return self.trial_list[trial_nr]


if __name__ == "__main__":
    stimulus_range = [-10, -5, 0, 5, 10]
    repeats = [2, 3, 4, 3, 2]
    cond = {"frame_angles": [22.5, 33.75], "currents": [0.0, 1.0]}
    s = RandStim(stimulus_range, repeats, **cond)
    print(s.trial_list)
    print(np.shape(s.trial_list))
