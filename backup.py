# TODO: got a bit overzealous, implement this later as a separate NetworkManager / in State
# def _start_server(self):
#     self._logger.info("[SERVER] Starting...")
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind(("0.0.0.0", self._PORT))
#         s.listen()
#         self._logger.info(f"[SERVER] Listening on port {self._PORT}")
#         while True:
#             conn, addr = s.accept()
#
# def _try_connect_peer(self, peer):
#     """Start client mode, if no server present, promote self to server."""
#     self._logger.info("[CLIENT] Attempting to connect ...")
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.settimeout(2)  # timeout before connection
#         try:
#             s.connect((peer, self._PORT))
#             self._logger.info("[CLIENT] Connected to {peer}")
#             s.sendall(b"Hello from client")
#             response = s.recv(1024)
#             print(f"[CLIENT] Received: {response.decode()}")
#             return True
#         except (ConnectionRefusedError, TimeoutError):
#             self._logger.info(f"[CLIENT] No server at {peer}")
#             return False
#
# def _start_peer_mode(self):
#     """Start client mode, try all peers, if no server present, promote self to server."""
#     for peer in self.PEER_IPS:
#         if self._try_connect_peer(peer):
#             return  # Found a server, stop trying
#         self._logger.info("[CLIENT] No servers found - promoting to server...")
#         self._start_server()
#
# def _discover_peers(self):
#     peers = []
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#         s.settimeout(3)
#
#         message = b"Discover peers"
#         s.sendto(message, ("<broadcast>", 12345))
#
#         start_time = time.time()
#         while time.time() - start_time < 10:
#             try:
#                 _, addr = s.recvfrom(1024)
#                 peers.append(addr)
#             except TimeoutError:
#                 break
#
#         self._logger.debug(f"Discovered {len(peers)} peer(s): {peers}")
#     return peers

