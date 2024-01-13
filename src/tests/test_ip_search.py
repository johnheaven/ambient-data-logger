import asyncio
import ipaddress
import json
import time
import logging
from os import path
from typing import Iterable

import pytest, pytest_asyncio
import httpx
import pytest_httpx

from ..helpers.ip_search import IPSearch

## SETUP

first = "192.168.2.101"
last = "192.168.2.200"

### FIXTURES ###

@pytest.fixture
def ip_iter() -> Iterable[str]:
    return IPSearch.ip_iter(first, last)
    
## TESTS ###

# IP Iterator #

def test_iter_length(ip_iter):
    assert len(list(ip_iter)) == 100

def test_ip_iter_next(ip_iter):
    assert str(next(ip_iter)) == first

def test_ip_iter_middle(ip_iter):
    assert ipaddress.IPv4Address("192.168.2.150") in list(ip_iter)

def test_ip_iter_last(ip_iter):
    assert last == str(tuple(ip_iter)[-1])

# Check IP and build queue #

@pytest.mark.asyncio
async def test_check_ip(httpx_mock):
    test_ip = "192.168.2.1"
    httpx_mock.add_response(url=f"http://{ test_ip }")
    httpx_mock.add_exception(httpx.TimeoutException("Timeout"))
    assert test_ip == await IPSearch.check_ip_exists(test_ip, httpx_obj=httpx)
    assert None is await IPSearch.check_ip_exists("192.168.2.2", httpx_obj=httpx)

@pytest_asyncio.fixture
async def ip_queue(ip_iter, httpx_mock):
    queue_out = asyncio.Queue()
    httpx_mock.add_response(url="http://192.168.2.101")
    httpx_mock.add_exception(httpx.TimeoutException("Timeout"))
    task = asyncio.create_task(IPSearch.populate_ip_queue(queue_in=ip_iter, queue_out=queue_out, httpx_obj=httpx))
    await asyncio.sleep(0.5)
    task.cancel()

    return queue_out
    
@pytest.mark.asyncio
async def test_populate_ip_queue(ip_queue):
    assert 1 == ip_queue.qsize()
    results = ip_queue.get_nowait()
    assert str(results) == "192.168.2.101"

# IP to path #

@pytest.mark.asyncio
async def test_ip_to_path():
    assert await IPSearch.ip_to_path("192.168.2.101") == "http://192.168.2.101/data"

@pytest_asyncio.fixture
async def paths_queue(ip_queue):
    queue_out = asyncio.Queue()
    task = asyncio.create_task(IPSearch.ips_to_paths(queue_in=ip_queue, queue_out=queue_out))
    await asyncio.sleep(0.5)
    task.cancel()
    return queue_out

@pytest.mark.asyncio
async def test_ips_to_paths(paths_queue):
    assert isinstance(paths_queue, asyncio.Queue)
    assert paths_queue.get_nowait() == "http://192.168.2.101/data"

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


@pytest_asyncio.fixture
async def payloads_queue(paths_queue, httpx_mock):
    httpx_mock.add_response(url="http://192.168.2.101/data", json='{"pico_id": "something or other", "temp": "1234"}')
    queue_out = asyncio.Queue()
    # run the task
    task = asyncio.create_task(IPSearch.get_payloads(queue_in=paths_queue, queue_out=queue_out, timeout=0.5, httpx_obj=httpx))
    # wait for half a second before cancelling it (otherwise it runs infinitely)
    await asyncio.sleep(0.5)
    task.cancel()
    return queue_out


@pytest.mark.asyncio
async def test_payloads(payloads_queue):
    # just a placeholder to pull in payloads from fixture to see if it works
    assert 1 == payloads_queue.qsize()

@pytest.mark.asyncio
async def test_payloads_type(payloads_queue):
    assert isinstance(payloads_queue, asyncio.Queue)

# FILTER #

@pytest.mark.asyncio
async def test_filter_payload():
    assert await IPSearch.filter_payload(None) is None
    assert await IPSearch.filter_payload({"pico_id": "something"}) == {"pico_id": "something"}
    assert await IPSearch.filter_payload({"random data": "random data"}) is None
