import logging
import subprocess
from typing import ClassVar

from logic.states import (
    Bootstrapping,
    ClientAndServer,
    ClientOnly,
    Promoting,
    Relinquishing,
    State,
)

logging.basicConfig(level=logging.DEBUG)


def get_tailscale_ip() -> str:
    result = subprocess.run(
        ["tailscale", "ip", "-4"], check=False, capture_output=True, text=True
    )
    return result.stdout.strip()


class DaemonContext:
    ALLOWED_STATES: ClassVar[list] = [
        Bootstrapping,
        ClientOnly,
        Promoting,
        ClientAndServer,
        Relinquishing,
    ]

    def __init__(self) -> None:
        self._logger = logging.getLogger(type(self).__name__)
        self._LOCAL_IP = get_tailscale_ip()
        self._PORT = 9876
        self._PROBE_TIMEOUT = 20000
        self._HEARTBEAT_INTERVAL = 1000
        self._HEARTBEAT_TIMEOUT = 10000

        self._active_server_ip = None
        self.last_server_heartbeat = 0
        self._is_server_active = False

        self._http_session = None
        self._active_battles = {}

        self._current_state = Bootstrapping(self)

        self._server_flag = False

        # self.PEER_IPS = self._discover_peers()
        self.PEER_IPS = []

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, next_state: type[State]):
        if next_state not in self.ALLOWED_STATES:
            raise ValueError
        self._current_state = next_state(self)

    def transition_to(self, new_state: type[State]):
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

    def start(self):
        pass

    def stop(self):
        pass
