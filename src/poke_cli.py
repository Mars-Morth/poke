#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Automatically run within the Poke virtual environment if not already active
_venv_python = Path(__file__).resolve().parent / "venv" / "bin" / "python"
if not _venv_python.is_file():
    _opt_venv = Path.home() / "opt" / "poke" / "src" / "venv" / "bin" / "python"
    if _opt_venv.is_file():
        _venv_python = _opt_venv

if _venv_python.is_file() and sys.executable != str(_venv_python):
    os.execv(str(_venv_python), [str(_venv_python), str(Path(__file__).resolve())] + sys.argv[1:])

_src_dir = str(Path(__file__).resolve().parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import argparse
import asyncio

import aiohttp


async def fetch_data(session, url):
    print(f"Starting task: {url}")
    async with session.get(url) as response:
        await asyncio.sleep(1)  # Simulating a delay
        data = await response.json()
        print(f"Completed task: {url}")
        return data


async def main():
    url = "http://npn-s03317.taile7fded.ts.net:9876/server"  # TEST: this is hardcoded

    async with aiohttp.ClientSession() as session:
        # tasks = [fetch_data(session, url) for url in url]
        tasks = fetch_data(session, url)
        results = await asyncio.gather(tasks)

        for result in results:
            print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poké CLI")
    parser.parse_args()
    asyncio.run(main())
