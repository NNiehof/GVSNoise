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
        self.block_size = block_size
        self.trial_list = []
        self.trials = []
        self.gvs_missed = []
        self.no_gvs_missed = []
        for curr in currents:
            for stim, repeat in zip(stimulus_range, repeats):
                for rep in range(repeat):
                    if len(frame_angles) > 1:
                        for frame in frame_angles:
                            self.trials.append([stim, frame, curr])
                    else:
                        # this is to avoid iterating over letters when the
                        # only condition is "noframe" (string)
                        self.trials.append([stim, frame_angles, curr])
        # split trial list in half over GVS current condition
        # TODO: make this flexible for > 2 current conditions
        half = int(len(self.trials) / 2)
        first_half = self.trials[0:half]
        shuffle(first_half)
        second_half = self.trials[half::]
        shuffle(second_half)
        self.alternate_blocks(first_half, second_half)

    def alternate_blocks(self, cond1_trials, cond2_trials):
        """
        Alternate conditions blockwise
        :param cond1_trials:
        :param cond2_trials:
        """
        n_blocks = int((len(cond1_trials) + len(cond2_trials)
                        / self.block_size))
        for block in range(n_blocks):
            i_start = block * self.block_size
            i_end = (block + 1) * self.block_size
            sublist = cond1_trials[i_start:i_end]
            for item in sublist:
                self.trial_list.append(item)
            sublist = cond2_trials[i_start:i_end]
            for item in sublist:
                self.trial_list.append(item)

    def get_stimulus(self, trial_nr):
        """
        Return stimulus and conditions for next trial
        :return trial: list with [stimulus_value, conditions]
        """
        return self.trial_list[trial_nr]

    def trial_missed(self, trial):
        """
        Add missed trials to list for repeating later
        :param trial:
        """
        if trial[2] == 0:
            self.no_gvs_missed.append(trial)
        else:
            self.gvs_missed.append(trial)

    def rerun_missed_trials(self):
        self.alternate_blocks(self.gvs_missed, self.no_gvs_missed)
        # NOTE: account for variable lengths lists


if __name__ == "__main__":
    stim_range = [5, 4, 3, 2]
    repeats = [2, 2, 2, 2]
    cond = {"frame_angles": ["noframe", 20.0], "currents": [0.0, 1.0],
            "block_size": 4}
    s = BlockStim(stim_range, repeats, **cond)
    print(s.trial_list)
    print(len(s.trial_list))
