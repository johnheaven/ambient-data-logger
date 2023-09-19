import asyncio

from ip_search.ip_search import IPSearch
from readings_to_tuples.readings_to_tuples import ReadingsToTuples

async def ambient_data_pipeline(first: str, last: str):
    payloads = await IPSearch.pipeline(first, last)
    db_tuples = await ReadingsToTuples.pipeline(payloads)

    print(db_tuples)

if __name__ == "__main__":
    asyncio.run(ambient_data_pipeline("192.168.2.121", "192.168.2.150"))