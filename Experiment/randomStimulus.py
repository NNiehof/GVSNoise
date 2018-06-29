from random import shuffle
import numpy as np


class RandStim:

    def __init__(self, stimulus_range=None, repeats=None, frame_angles=None,
                 currents=None):
        """
        Object that creates a randomised list of trials, out of a range of
        stimulus values and conditions.
        :param stimulus_range: range
        :param repeats: number of repeats per combination
        :param frame_angles: tilts in degrees
        :param currents: maximum current in mA
        """
        self.trial_list = []
        for stim, repeat in zip(stimulus_range, repeats):
            for rep in range(repeat):
                for frame in frame_angles:
                    for curr in currents:
                        self.trial_list.append([stim, frame, curr])
        shuffle(self.trial_list)

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
