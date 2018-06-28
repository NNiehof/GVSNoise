from abc import ABC, abstractmethod
from numpy import repeat


class GetNextTrial(ABC):

    @abstractmethod
    def __init__(self, stimulus_range, repeats):
        """

        :param stimulus_range: list
        :param repeats: int, or list with same length as stimulus_range
        """
        self.probes = repeat(stimulus_range, repeats)

    @abstractmethod
    def get_stimulus(self, trial_nr):
        """
        Return a stimulus value to be presented in the specified trial.
        """

