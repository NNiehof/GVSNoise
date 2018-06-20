from abc import ABC, abstractmethod


class GetNextTrial(ABC):

    @abstractmethod
    def __init__(self, stimulus_range, conditions):
        self.stimulus_range = stimulus_range
        if not isinstance(conditions, list):
            raise(TypeError("conditions must be a list"))
        self.conditions = conditions

    @abstractmethod
    def get_stimulus(self):
        """
        Return a stimulus value to be presented in the next trial.
        """

