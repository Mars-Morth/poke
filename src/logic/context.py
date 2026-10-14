import ipaddress


class DaemonContext:
    def __init__(self) -> None:
        self._LOCAL_IP = ipaddress.IPv4Address
        self._PORT = 9876
        self._PEER_IPS = []
        self._PROBE_TIMEOUT = 20000
        self._HEARTBEAT_INTERVAL = 1000
        self._HEARTBEAT_TIMEOUT = 10000

        self._active_server_ip = None
        self.last_server_heartbeat = 0
        self._is_server_active = False

        self._http_session = None
        self._active_battles = {}

        self._current_state = None

    async def transition_to(self, new_state):
        await self.current_state.exit()

    def start():
        pass

    def stop():
        pass
