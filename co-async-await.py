import asyncio
import time

#'async def' creates a coroutine object, not execution.
async def task(name, delay):
    print(f"{name} started at {time.time():.2f}")
    await asyncio.sleep(delay)
    print(f"{name} finished at {time.time():.2f}")

'''
Event loop - the executor, not the coroutine.
Only way to execute async function'''
async def main():
    await asyncio.gather(
        task("A", 10),
        task("B", 1),
        task("C", 2),
    )

# creates and starts event loop
asyncio.run(main())
