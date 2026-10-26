import asyncio
import logging
from typing import ClassVar

from logic.states import (
    Bootstrapping,
    ClientAndServer,
    ClientOnly,
    Promoting,
    Relinquishing,
    State,
    StateTransitionError,
)
from utils import network

logging.basicConfig(level=logging.DEBUG)


class DaemonContext:
    ALLOWED_STATES: ClassVar[list] = [
        Bootstrapping,
        ClientOnly,
        Promoting,
        ClientAndServer,
        Relinquishing,
    ]

    async def __init__(self) -> None:
        self._logger = logging.getLogger(type(self).__name__)
        self._LOCAL_IP = await asyncio.to_thread(network.get_tailscale_ip)
        self.PORT = 9876
        self._PROBE_TIMEOUT = 20000
        self._HEARTBEAT_INTERVAL = 1000
        self._HEARTBEAT_TIMEOUT = 10000

        self.active_server_ip: str | None = None
        self.last_server_heartbeat = 0
        self._is_server_active = False

        self._http_session = None
        self._active_battles = {}

        self._current_state = Bootstrapping(self)

        self._server_flag = False

        self.PEER_IPS = await asyncio.to_thread(network.discover_peers)

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, next_state: type[State]):
        if next_state not in self._current_state.allowed_states:
            raise StateTransitionError(
                f"Unsupported transition between {self._current_state!r} and {next_state!r}"
            )
        self._current_state = next_state(self)

    async def transition_to(self, new_state: type[State]):
        await self.current_state.exit()
        self.current_state = new_state
        await self.current_state.enter()

    def start(self):
        pass

    def stop(self):
        pass
