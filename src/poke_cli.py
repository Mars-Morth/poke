#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys

import aiohttp

LOGGER = logging.getLogger(__name__)
DAEMON_BASE = "http://127.0.0.1:9876"  # TEST: hardcoded to localhost


async def fetch_data(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def run(args):
    LOGGER.debug("Called with args: %s", args)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        if args.command == "serve":
            async with session.post(f"{DAEMON_BASE}/client/serve") as response:
                response.raise_for_status()
                serve_result = await response.json()
                LOGGER.debug("Daemon serve response: %s", serve_result)

        result = await fetch_data(session, f"{DAEMON_BASE}/server")
        print(result)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="poke", description="Poké CLI")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug logging"
    )
    commands = parser.add_subparsers(dest="command")
    serve = commands.add_parser("serve", help="advertise your Poké daemon as a server")
    serve.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="enable debug logging",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        asyncio.run(run(args))
    except aiohttp.ClientConnectionError:
        print(f"poke: cannot connect to daemon at {DAEMON_BASE}", file=sys.stderr)
        return 1
    except asyncio.TimeoutError:
        print("poke: daemon request timed out", file=sys.stderr)
        return 1
    except (aiohttp.ClientError, ValueError) as exc:
        print(f"poke: daemon request failed: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
