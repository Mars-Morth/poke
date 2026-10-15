#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Determine the Poke source directory
_file_path = Path(__file__).resolve()
_src_dir = None
for candidate in [
    _file_path.parent,
    _file_path.parent.parent.parent,
    Path.home() / "opt" / "poke" / "src",
]:
    if (candidate / "logic").is_dir():
        _src_dir = candidate
        break

if _src_dir is not None and str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

# Determine the Poke virtualenv Python
_venv_python = None
for candidate in [
    _file_path.parent / "python",
    _file_path.parent / "venv" / "bin" / "python",
    (_src_dir / "venv" / "bin" / "python") if _src_dir else None,
    Path.home() / "opt" / "poke" / "src" / "venv" / "bin" / "python",
]:
    if candidate and candidate.is_file():
        _venv_python = candidate
        break

# Automatically run within the Poke virtual environment if not already active
if _venv_python and sys.executable != str(_venv_python):
    os.execv(
        str(_venv_python),
        [str(_venv_python), str(_file_path)] + sys.argv[1:],
    )

import argparse
import asyncio
import logging

import aiohttp

logging.basicConfig(level=logging.DEBUG)  # TEST: enable debug logging
LOGGER = logging.getLogger()


async def fetch_data(session, url):
    print(f"Starting task: {url}")
    async with session.get(url) as response:
        await asyncio.sleep(1)  # Simulating a delay
        data = await response.json()
        print(f"Completed task: {url}")
        return data


async def main(args):
    LOGGER.debug(f"Called main with args: {args}")

    daemon_base = "http://127.0.0.1:9876"
    server_url = f"{daemon_base}/server/"

    async with aiohttp.ClientSession() as session:
        if args.serve:
            async with session.post(f"{daemon_base}/daemon/serve") as response:
                serve_result = await response.json()
                LOGGER.debug(f"Daemon serve response: {serve_result}")

        tasks = fetch_data(session, server_url)
        results = await asyncio.gather(tasks)

        for result in results:
            print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="poke", description="Poké CLI")
    parser.add_argument(
        "serve",
        nargs="?",
        default=None,
        help="advertise your Poké daemon as a server",
    )

    args = parser.parse_args()
    asyncio.run(main(args))
