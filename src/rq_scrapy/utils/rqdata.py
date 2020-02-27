from scrapy.http.request import Request

try:
    import ujson as json
except:
    import json

def queues_from_rq(queues_json):
    return json.loads(queues_json)

def request_from_rq(
    request_json,
    callback=None,
    errback=None,
    dont_filter=True,
    priority=0,
    flags=None,
    cb_kwargs=None,
):
    r = json.loads(request_json)
    return Request(
        url=r["url"],
        method=r.get("method", "GET"),
        meta=r.get("meta", None),
        headers=r.get("headers", None),
        cookies=r.get("cookies", None),
        body=r.get("body", None),
        encoding=r.get("encoding", None),
        dont_filter=dont_filter,
        callback=callback,
        errback=errback,
        priority=priority,
        flags=flags,
        cb_kwargs=cb_kwargs,
    )
