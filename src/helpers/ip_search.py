import ipaddress
import asyncio
from os import path
import logging
from typing import Iterable, Iterator
from itertools import chain

import httpx

from .helpers import worker, async_chain

class IPSearch:
    @staticmethod
    async def pipeline(queue_in: asyncio.Queue, queue_out: asyncio.Queue, n_workers=20, log_output=False) -> None:
        # instantiate all the workers and connect them up
        
        async with asyncio.TaskGroup() as tg:
            tasks = await async_chain(
                (IPSearch.populate_ip_queue, 100),
                IPSearch.ips_to_paths,
                (IPSearch.get_payloads, 20),
                IPSearch.filter_payloads,
                queue_in=queue_in,
                queue_out=queue_out,
                tg=tg
            )
  
    @staticmethod
    def ip_iter(first: str, last: str) -> Iterable:
        range = (
            ipaddress.IPv4Address(first),
            ipaddress.IPv4Address(last)
        )
        networks = ipaddress.summarize_address_range(*range)

        ip_iter = chain(*networks)

        return ip_iter

    @staticmethod
    async def check_ip_exists(ip: str | ipaddress.IPv4Address, httpx_obj=httpx, timeout=4):
        # check ip and add to the queue if they exist on the network
        try:
            async with httpx_obj.AsyncClient() as client:
                await client.get(url=f"http://{ str(ip) }", timeout=httpx.Timeout(timeout=timeout))
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            pass
        else:
            return ip
    
    populate_ip_queue = worker(check_ip_exists, add_none=False)

    @staticmethod
    async def ip_to_path(ip):
        device_path = path.join("http://", str(ip), "data")
        return device_path
    ips_to_paths = worker(ip_to_path)


    @staticmethod
    async def get_payload(device_path, httpx_obj=httpx, timeout=5, **kwargs) -> list | dict | None:
        # get a payload from device path e.g. http://192.168.2.1/data
        try:
            async with httpx_obj.AsyncClient() as client:
                response = await client.get(url=device_path, timeout=httpx.Timeout(timeout=timeout))
                assert response.status_code == 200
                payload = response.json()
        except Exception as e:
            # couldn't connect at all, didn't get a 200 response code, or couldn't convert response to json
            payload = None
        return payload
    get_payloads = worker(get_payload)

    @staticmethod
    async def filter_payload(payload: dict):
        return payload if payload and "pico_id" in payload else None
    filter_payloads = worker(filter_payload, add_none=False)

if __name__ == "__main__":
    asyncio.run(IPSearch.pipeline("192.168.2.100", "192.168.2.200"))