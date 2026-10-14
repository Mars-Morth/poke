import asyncio
import time

import aiohttp


async def fetch_data(session, url):
    print(f"Starting task: {url}")
    async with session.get(url) as response:
        await asyncio.sleep(1)  # Simulating a delay
        data = await response.json()
        print(f"Completed task: {url}")
        return data


async def main():
    url = "https://npn-s03320.taile7fded.ts.net/"

    async with aiohttp.ClientSession() as session:
        # tasks = [fetch_data(session, url) for url in url]
        tasks = fetch_data(session, url)
        results = await asyncio.gather(tasks)

        for result in results:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
