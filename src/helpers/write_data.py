import asyncio
from .helpers import worker, async_chain, show_outputs
import csv
import functools

class WriteData:
    @staticmethod
    async def pipeline(queue_in: asyncio.Queue, queue_out: asyncio.Queue, csv_path: str):
        async with asyncio.TaskGroup() as tg:
            await async_chain(
                functools.partial(WriteData.csv_write, csv_path=csv_path, flush_every=10),
                queue_in=queue_in,
                queue_out=queue_out,
                tg=tg
        )

    ### KEEP CONNECTION ALIVE ###

    async def check_and_reconnect(connection):
        pass

    ### CSV ###

    @staticmethod
    async def reading_to_csv(data: tuple, csv_writer):
        csv_writer.writerow(data)
        return data
    readings_to_csv = worker(reading_to_csv)

    @staticmethod
    async def regular_flush(f, flush_every):
        # flush the file object on a regular basis
        while True:
            f.flush()
            await asyncio.sleep(flush_every)

    @staticmethod
    async def csv_write(queue_in, queue_out, csv_path: str, flush_every: int):
        # wrapper to open the file so we don't have to reopen it for every reading
        with open(csv_path, "a") as f:
            csv_writer = csv.writer(f)
            async with asyncio.TaskGroup() as tg:
                tg.create_task(
                    WriteData.readings_to_csv(queue_in, queue_out, csv_writer=csv_writer),
                    )
                tg.create_task(WriteData.regular_flush(f, flush_every))

    ### SQL ###
