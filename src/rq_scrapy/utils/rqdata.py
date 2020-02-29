from urllib.parse import urljoin

import aiohttp
import async_timeout
from scrapy.http.request import Request

try:
    import ujson as json
except:
    import json


async def queues_from_rq(api, k=16, timeout=0):
    status, ret, api_url = await queues_json_from_rq(api, k, timeout)
    if status == 200:
        ret = json_to_queues(ret)
    return status, ret, api_url


async def request_from_rq(
    api,
    qid,
    timeout=0,
    callback=None,
    errback=None,
    dont_filter=True,
    priority=0,
    flags=None,
    cb_kwargs=None,
):
    status, ret, api_url = await request_json_from_rq(api, qid, timeout=timeout)
    if status == 200:
        ret = json_to_request(
            ret,
            callback=callback,
            errback=errback,
            dont_filter=dont_filter,
            priority=priority,
            flags=flags,
            cb_kwargs=cb_kwargs,
        )
    return status, ret, api_url


async def get_from_rq(request_url, timeout=0):
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(timeout):
            async with session.get(request_url) as response:
                status = response.status
                text = await response.text()
                return status, text.strip()


async def request_json_from_rq(api, qid, timeout=0):
    api_url = urljoin(api, "request/recv/?q=%s" % qid)
    status, ret = await get_from_rq(api_url, timeout=timeout)
    return status, ret, api_url


async def queues_json_from_rq(api, k=10, timeout=0):
    api_url = urljoin(api, "rq/queues/?k=%d" % k)
    status, ret = await get_from_rq(api_url, timeout=timeout)
    return status, ret, api_url


def json_to_queues(queues_json):
    return json.loads(queues_json)


def json_to_request(
    request_json,
    callback=None,
    errback=None,
    dont_filter=True,
    priority=0,
    flags=None,
    cb_kwargs=None,
):
    response = json.loads(request_json)
    r = json.loads(response["request"])
    return Request(
        url=r["url"],
        method=r.get("method", "GET"),
        meta=r.get("meta", None),
        headers=r.get("headers", None),
        cookies=r.get("cookies", None),
        body=r.get("body", None),
        encoding=r.get("encoding", "utf-8"),
        dont_filter=dont_filter,
        callback=callback,
        errback=errback,
        priority=priority,
        flags=flags,
        cb_kwargs=cb_kwargs,
    )
