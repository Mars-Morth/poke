# TODO: consolidate network utils (https://github.com/Mars-Morth/poke/issues/21)

import asyncio
import subprocess
from ipaddress import ip_address

import aiohttp

from logic.states import ClientAndServer

_tailscale_ip: str | None = None


def get_tailscale_ip() -> str:
    global _tailscale_ip

    if _tailscale_ip is not None:
        return _tailscale_ip

    result = subprocess.run(
        ["tailscale", "ip", "-4"], check=True, capture_output=True, text=True
    )
    _tailscale_ip = result.stdout.strip()
    return _tailscale_ip


def discover_peers() -> list[str]:
    result = subprocess.run(
        ["tailscale", "status", "--active"],
        check=True,
        capture_output=True,
        text=True,
    )

    local_ip = get_tailscale_ip()

    return [
        parts[0]
        for line in result.stdout.splitlines()
        if (parts := line.split()) and parts[0] != local_ip
    ]


async def _probe_peer(
    session: aiohttp.ClientSession, peer_ip: str, port: int
) -> str | None:
    try:
        endpoint = "server"
        async with session.get(f"http://{peer_ip}:{port}/{endpoint}") as response:
            response.raise_for_status()
            data = await response.json()

        if isinstance(data, dict) and data.get("role") == ClientAndServer.name:
            return peer_ip
    except (TimeoutError, aiohttp.ClientError, ValueError):
        pass  # Peer unavailable or response invalid

    return None


async def discover_server(peer_ips: list[str], port: int = 9876) -> str | None:
    timeout = aiohttp.ClientTimeout(total=3)  # Seconds per request

    async with aiohttp.ClientSession(timeout=timeout) as session:
        results = await asyncio.gather(
            *(_probe_peer(session, peer_ip, port) for peer_ip in peer_ips)
        )

    servers = [peer_ip for peer_ip in results if peer_ip is not None]
    return min(servers, key=ip_address, default=None)
