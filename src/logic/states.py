from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self, state):
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @abstractmethod
    def enter(self, state):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def process(self):
        pass


class Bootstrapping(State):
    pass


class ClientOnly(State):
    pass


class Promoting(State):
    pass


class ClientAndServer(State):
    pass


class Relinquishing(State):
    pass
