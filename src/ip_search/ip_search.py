import ipaddress
import asyncio
from os import path
import logging
from typing import Iterable
from itertools import chain

import httpx

logging.basicConfig(level=logging.INFO)

class IPSearch:
    @staticmethod
    async def pipeline(first: str, last: str) -> Iterable:
        ip_iter = IPSearch.ip_iter(first, last)
        payloads = await IPSearch.get_payloads(ip_iter)
        payloads = IPSearch.filter_payloads(payloads)
        logging.info(payloads)
        return payloads

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
    async def get_payload(device_path: str, httpx_obj=httpx, timeout=5) -> list | dict | None:
        try:
            async with httpx_obj.AsyncClient() as client:
                response = await client.get(url=device_path, timeout=httpx.Timeout(timeout=timeout))
                assert response.status_code == 200
                payload = response.json()
        except Exception as e:
            # couldn't connect at all, didn't get a 200 response code, or couldn't convert response to json
            payload = None
        
        logging.debug(f"device_path: { device_path }")
        if payload: logging.debug(f"Payload: { payload }")
        return payload

    @staticmethod
    async def get_payloads(ips, timeout=5) -> Iterable:
        async with asyncio.TaskGroup() as tg:
            payload_tasks = [
                tg.create_task(IPSearch.get_payload(
                    path.join("http://", str(ip), "data"), httpx, timeout
                    )) for ip in ips
                ]
        return await asyncio.gather(*payload_tasks)

    @staticmethod
    def filter_payloads(payloads) -> Iterable:
        return tuple(filter(bool, payloads))


if __name__ == "__main__":
    asyncio.run(IPSearch.pipeline("192.168.2.100", "192.168.2.200"))