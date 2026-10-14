from abc import ABC, abstractmethod

from context import DaemonContext


class State(ABC):
    def __init__(self, context: DaemonContext):
        self.context = context

    def __str__(self) -> str:
        return self.name

    @property
    def name(self):
        return type(self).__name__

    # @abstractmethod
    def enter(self):
        pass

    # @abstractmethod
    def exit(self):
        pass

    # @abstractmethod
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
