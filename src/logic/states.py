from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self, context):
        self.context = context
        self.name = "State"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @abstractmethod
    def enter(self, name):
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
