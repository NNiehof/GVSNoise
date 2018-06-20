from random import shuffle
from Experiment.getTrial import GetNextTrial


class RandStim(GetNextTrial):

    def __init__(self, stimulus_range, conditions):
        GetNextTrial.__init__(self, stimulus_range, conditions)
        # trial list with all combinations of stimulus values and conditions
        self.triallist = []
        for stim in self.stimulus_range:
            for cond in self.conditions:
                self.triallist.append([stim, cond])
        shuffle(self.triallist)
        self.count = 0

    def get_stimulus(self):
        """
        Return stimulus and conditions for next trial
        :return trial: list with [stimulus_value, conditions]
        """
        trial = self.triallist[self.count]
        self.count += 1
        return trial


