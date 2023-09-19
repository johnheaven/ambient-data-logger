import json
import asyncio
import ipaddress
from os import path
from typing import Iterable
import logging

import pytest
from pytest import fixture
import httpx
import pytest_httpx


from ip_search.ip_search import IPSearch

## SETUP

first = "192.168.2.101"
last = "192.168.2.200"

### FIXTURES ###

@fixture
def ips() -> Iterable[str]:
    return IPSearch.ip_iter(first, last)
    
## TESTS ###

# IPS #

def test_ips_type(ips):
    assert isinstance(ips, Iterable)

def test_ips_next(ips):
    next(ips)

def test_ips_first(ips):
    assert first == str(next(ips))

def test_ips_first_type(ips):
    assert isinstance(
        next(ips), ipaddress.IPv4Address
        )

def test_ips_last(ips):
    assert last == str(tuple(ips)[-1])

# DATA RETRIEVAL #

@pytest.mark.asyncio
async def test_get_payload_error(httpx_mock):

    httpx_mock.add_response()

    # run the test

    assert not (await IPSearch.get_payload(device_path="http://192.168.2.50/data", httpx_obj=httpx))

@pytest.mark.asyncio
async def test_payload_json_success(httpx_mock):
    ip = "192.168.2.105"
    device_path = path.join("http://", ip, "data")
    httpx_mock.add_response(
        url=device_path,
        status_code=200,
        json=json.loads('{"pressure": null, "sensor": "dht22", "pico_id": "office", "pico_uuid": "5mFBA+c0kiQ=", "humidity": 69.1, "temp": 21.9}')
        )
    
    # run the tests
    result = await IPSearch.get_payload(device_path=device_path, httpx_obj=httpx)

    assert result == json.loads('{"pressure": null, "sensor": "dht22", "pico_id": "office", "pico_uuid": "5mFBA+c0kiQ=", "humidity": 69.1, "temp": 21.9}')

@fixture
def payloads(ips):
    return asyncio.run(IPSearch.get_payloads(ips, timeout=0.5))

@pytest.mark.asyncio
async def test_payloads(payloads):
    # just a placeholder to pull in payloads from fixture to see if it works
    pass

@pytest.mark.asyncio
async def test_payloads_type(payloads):
    assert isinstance(payloads, Iterable)

# FILTER #

def test_payloads_filtered():
    payloads = [None, None, "{'Some': 'json'}"]
    assert tuple(IPSearch.filter_payloads(payloads)) == ("{'Some': 'json'}",)
