from random import shuffle
import numpy as np


class BlockStim:

    def __init__(self, stimulus_range=None, repeats=None, frame_angles=None,
                 currents=None, block_size=None):
        """
        Object that creates a randomised list of trials, out of a range of
        stimulus values and conditions.
        :param stimulus_range: range
        :param repeats: number of repeats per combination
        :param frame_angles: tilts in degrees
        :param currents: maximum current in mA
        """
        trials = []
        for curr in currents:
            for stim, repeat in zip(stimulus_range, repeats):
                for rep in range(repeat):
                    for frame in frame_angles:
                        trials.append([stim, frame, curr])
        # split trial list in half over GVS current condition
        half = int(len(trials) / 2)
        first_half = trials[0:half]
        shuffle(first_half)
        second_half = trials[half:-1]
        shuffle(second_half)

        # alternate current conditions
        n_blocks = int(len(trials) / block_size)
        self.trial_list = []
        for block in range(n_blocks):
            i_start = block * block_size
            i_end = (block + 1) * block_size
            sublist = first_half[i_start:i_end]
            for item in sublist:
                self.trial_list.append(item)
            sublist = second_half[i_start:i_end]
            for item in sublist:
                self.trial_list.append(item)

    def get_stimulus(self, trial_nr):
        """
        Return stimulus and conditions for next trial
        :return trial: list with [stimulus_value, conditions]
        """
        return self.trial_list[trial_nr]


if __name__ == "__main__":
    stimulus_range = [-10, -5, 0, 5, 10]
    repeats = [3, 3, 3, 3, 3]
    cond = {"frame_angles": [22.5, 33.75], "currents": [0.0, 1.0],
            "block_size": 3}
    s = BlockStim(stimulus_range, repeats, **cond)
    print(s.trial_list)
    print(np.shape(s.trial_list))
