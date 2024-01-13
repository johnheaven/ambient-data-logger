import json
from datetime import datetime as dt
import asyncio
from typing import Iterable

from .helpers import worker, async_chain

class PayloadsToTuples:
    @staticmethod
    async def pipeline(queue_in: asyncio.Queue, queue_out: asyncio.Queue):
        async with asyncio.TaskGroup() as tg:
            await async_chain(
                PayloadsToTuples.payloads_to_readings,
                queue_in=queue_in, queue_out=queue_out,
                tg=tg
            )
   
    @staticmethod
    async def payload_to_reading_collection(payload: dict) -> Iterable:
        metadata = payload["pico_id"], payload["pico_uuid"], payload["sensor"]
        reading_tuples = []
        # get tuples for temp, pressure, humidity
        reading_tuples = list(filter(lambda item: item[0] in ("temp", "pressure", "humidity"), payload.items()))
        # get them in order "temp, pressure, humidity"
        reading_tuples.sort(key=lambda t: t[0], reverse=True)

        reading_tuples = [(*metadata, *reading_tuple) for reading_tuple in reading_tuples]
        
        return reading_tuples
    payloads_to_readings = worker(payload_to_reading_collection, flatten=True)

    @staticmethod
    async def add_timestamp_to_reading(reading, datetime_obj=dt):
        now_str = datetime_obj.now().strftime("%Y-%m-%d %H:%M:%S")
        reading = (now_str, *reading)
        return reading

### add timestamp 
# 