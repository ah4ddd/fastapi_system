import asyncio
import string
import random
import time

sem = asyncio.Semaphore(3)  # only 3 tasks at once

async def task(name):
    async with sem:
        start = time.time()
        print(f"{name} STARTED at {start:.2f}")

        # simulate real I/O wait (DB / network)
        delay = random.uniform(1, 4)
        await asyncio.sleep(delay)

        end = time.time()
        print(f"{name} FINISHED at {end:.2f} (waited {delay:.2f}s)")

async def main():
    tasks = [task(letter) for letter in string.ascii_uppercase]  # A–Z
    await asyncio.gather(*tasks)

asyncio.run(main())
