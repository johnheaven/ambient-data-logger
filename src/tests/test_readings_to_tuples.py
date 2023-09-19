from datetime import datetime as dt

import pytest

from readings_to_tuples.readings_to_tuples import ReadingsToTuples

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "readings, database_tuples",
    [
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
    )
async def test_split_readings(readings, database_tuples):

    # set up datetime object -> can't use monkeypatch because this is immutable
    class FakeNow(dt):
        @staticmethod
        def now():
            # fake the .now function to pass into split_payloads
            return dt(2023, 3, 12, 13, 37, 5, 10398)

    # readings => database_tuples
    split_readings = await ReadingsToTuples.split_readings(readings=readings, datetime_obj=FakeNow)

    # nested tuples in form (timestamp, pico_id, pico_uuid, sensor, key, value) for each variable i.e. pressure, temperature and humidity separately
    assert sorted(split_readings, key=lambda item: str(item)) == sorted(database_tuples, key=lambda item: str(item))
