from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING

from utils import network

if TYPE_CHECKING:
    from context import DaemonContext


class StateTransitionError(ValueError):
    """Raised when a daemon state transition is invalid."""


class State(ABC):
    def __init__(self, context: DaemonContext):
        self.context = context

    def __str__(self) -> str:
        return self.name

    @abstractproperty
    def allowed_states(self):
        return []

    @property
    def name(self):
        return type(self).__name__

    @abstractmethod
    async def enter(self):
        pass

    @abstractmethod
    async def exit(self):
        pass

    @abstractmethod
    async def process(self):
        pass


class Bootstrapping(State):
    @property
    def allowed_states(self):
        return [ClientOnly, Promoting]

    async def enter(self):
        self.context.active_server_ip = await network.discover_server(
            self.context.PEER_IPS, self.context.PORT
        )

        if self.context.active_server_ip is not None:
            await self.context.transition_to(ClientOnly)
        else:
            await self.context.transition_to(Promoting)

    async def exit(self):
        pass

    async def process(self):
        # # TODO: Decide whether a client should nominate themselves, or automatically promote themselves to server if none found
        # self.context.active_server_ip = await network.discover_server(
        #     self.context.PEER_IPS, self.context.PORT
        # )
        #
        # if self.context.active_server_ip is not None:
        #     await self.context.transition_to(ClientOnly)
        #
        # # Otherwise, process again
        pass


class ClientOnly(State):
    @property
    def allowed_states(self):
        return [Promoting]

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def process(self):
        pass


class Promoting(State):
    @property
    def allowed_states(self):
        return [ClientAndServer]

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def process(self):
        pass


class ClientAndServer(State):
    @property
    def allowed_states(self):
        return [ClientAndServer, Relinquishing]

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def process(self):
        pass


class Relinquishing(State):
    @property
    def allowed_states(self):
        return [ClientAndServer]

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def process(self):
        pass
