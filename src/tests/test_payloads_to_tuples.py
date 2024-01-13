import asyncio
from datetime import datetime as dt

import pytest

from ..helpers.payloads_to_tuples import PayloadsToTuples

test_data = [
        ('{"pressure": null, "sensor": "dht22", "pico_id": "office", "pico_uuid": "5mFBA+c0kiQ=", "humidity": 66.9, "temp": 21.9}',
        (
            ("2023-03-12 13:37:05", "office", "5mFBA+c0kiQ=", "dht22", "pressure", None),
            ("2023-03-12 13:37:05", "office", "5mFBA+c0kiQ=", "dht22", "humidity", 66.9),
            ("2023-03-12 13:37:05", "office", "5mFBA+c0kiQ=", "dht22", "temp", 21.9)
        )),
        ('{"pressure": 2569.15, "sensor": "bme280", "pico_id": "bedroom", "pico_uuid": "5mFkCEMtfCM=", "humidity": 70.994, "temp": 19.83}',
        (
            ("2023-03-12 13:37:05", "bedroom", "5mFkCEMtfCM=", "bme280", "pressure", 2569.15),
            ("2023-03-12 13:37:05", "bedroom", "5mFkCEMtfCM=", "bme280", "humidity", 70.994),
            ("2023-03-12 13:37:05", "bedroom", "5mFkCEMtfCM=", "bme280", "temp", 19.83)
        ))
    ]

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, database_tuples",
    test_data
    )
async def test_payload_to_readings(payload, database_tuples):
    # strip the time stamps off the test data
    database_tuples = tuple((t[1:] for t in database_tuples))

    test_output = await PayloadsToTuples.payload_to_reading_collection(payload)

    # sort output to ensure a different order alone doesn't cause the assertion to fail
    assert sorted(test_output, key=lambda item: str(item)) == sorted(database_tuples, key=lambda item: str(item))

@pytest.mark.asyncio
async def test_add_timestamp():
    # set up datetime object -> can't use monkeypatch because this is immutable
    class FakeNow(dt):
        @staticmethod
        def now():
            # fake the .now function to pass into split_payloads
            return dt(year=2023, month=3, day=12, hour=13, minute=37, second=5, microsecond=10398)
    
    random_tuple = ("1", "2", "3", "4", "5")
    assert await PayloadsToTuples.add_timestamp_to_reading(random_tuple, datetime_obj=FakeNow) == ("2023-03-12 13:37:05", "1", "2", "3", "4", "5")
