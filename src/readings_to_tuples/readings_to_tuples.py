import json
from datetime import datetime as dt
import asyncio
from itertools import chain

class ReadingsToTuples:
    @staticmethod
    async def pipeline(payloads):
        tasks = []
        
        async with asyncio.TaskGroup() as tg:
            for payload in payloads:
                tasks.append(
                    tg.create_task(ReadingsToTuples.split_readings(payload))
                    )
        
        readings_tuples = await asyncio.gather(*tasks)
        # flatten tuples and return
        return tuple(chain(*readings_tuples))
    
    @staticmethod
    async def split_readings(readings: str | dict, datetime_obj=dt):
        if isinstance(readings, str): readings = json.loads(readings)
        reading_tuples = []
        now_str = datetime_obj.now().strftime("%Y-%m-%d %H:%M:%S")

        # get tuples for temp, pressure, humidity
        reading_tuples = list(filter(lambda item: item[0] in ("temp", "pressure", "humidity"), readings.items()))
        # get them in order "temp, pressure, humidity"
        reading_tuples.sort(key=lambda t: t[0], reverse=True)
        
        for i, reading_tuple in enumerate(reading_tuples):
            reading_tuples[i] = (
                (now_str, readings["pico_id"], readings["pico_uuid"], readings["sensor"], *reading_tuple)
            )
                
        return tuple(reading_tuples)
