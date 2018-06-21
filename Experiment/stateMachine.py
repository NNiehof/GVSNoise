"""
Finite State Machine based on:
 Title: Statemachine [code example]
 Author: Mertz, D.
 Date: 2000
 Code version: 1.0
 Availability: http://gnosis.cx/publish/programming/charming_python_4.txt
"""


class StateMachine(object):

    def __init__(self):
        self.handlers = {}
        self.startState = {}
        self.endStates = []
        self.logger = None

    def add_state(self, name, handler, end_state=False):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def add_logger(self, logger):
        self.logger = logger

    def set_start(self, name):
        self.startState = name.upper()

    def run(self):
        try:
            handler = self.handlers[self.startState]
        except:
            raise("InitializationError", "must call .set_start before .run()")
        if not self.endStates:
            raise("InitializationError", "at least one state must be an end_state")

        while True:
            new_state, go_next = handler()
            if new_state.upper() in self.endStates:
                break
            elif go_next:
                # progress to next state when go_next trigger is set to True
                if self.logger is not None:
                    self.logger.info("Next state: {}".format(new_state))
                else:
                    print("Next state: {}".format(new_state))
                handler = self.handlers[new_state.upper()]
            else:
                # loop in current state if the go_next trigger is set to False
                pass
