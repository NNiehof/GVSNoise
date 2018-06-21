from random import shuffle
from Experiment.getTrial import GetNextTrial


class RandStim(GetNextTrial):

    def __init__(self, stimulus_range, conditions):
        """
        Object that creates a randomised list of trials, out of a range of
        stimulus values and conditions.
        :param stimulus_range: range
        :param conditions: list
        """

        GetNextTrial.__init__(self, stimulus_range, conditions)
        # trial list with all combinations of stimulus values and conditions
        self.triallist = []
        for stim in self.stimulus_range:
            for cond in self.conditions:
                self.triallist.append([stim, cond])
        shuffle(self.triallist)

    def get_stimulus(self, trial_nr):
        """
        Return stimulus and conditions for next trial
        :return trial: list with [stimulus_value, conditions]
        """
        return self.triallist[trial_nr]
