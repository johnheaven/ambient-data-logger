import asyncio

from helpers.ip_search import IPSearch
from helpers.payloads_to_tuples import PayloadsToTuples
from helpers.write_data import WriteData
from helpers.helpers import async_chain, show_outputs
import functools

async def ambient_data_pipeline(first: str, last: str, csv_path:str):
    
    # get a generator with IPs (not strings but IPv4Address objects)
    ip_queue = asyncio.Queue()
    queue_out = asyncio.Queue()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(async_chain(
            IPSearch.pipeline,
            PayloadsToTuples.pipeline,
            show_outputs,
            functools.partial(WriteData.pipeline, csv_path=csv_path),
            queue_in=ip_queue,
            queue_out=queue_out,
            tg=tg
        ))

        delay = 20
        tg.create_task(populate_queue(queue=ip_queue, iterator_obj=IPSearch.ip_iter, iterator_args=(first, last), delay=delay))

async def populate_queue(queue, iterator_obj, delay, iterator_args=None):
    while True:
        n_items = 0
        for item in iterator_obj(*iterator_args):
            await queue.put(item)
            n_items += 1
        print(f"### ADDED { n_items } ITEMS TO QUEUE ###")
        await asyncio.sleep(delay)


if __name__ == "__main__":
    asyncio.run(ambient_data_pipeline("192.168.2.101", "192.168.2.200", csv_path="./test.csv"))