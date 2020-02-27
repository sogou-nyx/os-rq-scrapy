from rq_scrapy.utils.asyncio_defer import as_deferred
import aiohttp
import asyncio
import async_timeout
from urllib.parse import urljoin
from rq_scrapy.utils.rqdata import request_from_rq, queues_from_rq


class Scheduler(object):
    def __init__(self, rq_api, rq_timeout=10, stats=None, crawler=None):
        self.rq_api = rq_api
        self.rq_timeout = rq_timeout
        self.counter = 0
        self.crawler = crawler
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        rq_api = settings.get("RQ_API", "http://localhost:6789/")
        rq_timeout = settings.getint("RQ_TIMEOUT", 10)
        return cls(rq_api, rq_timeout, crawler.stats, crawler)

    async def get_request(self):
        async with aiohttp.ClientSession() as session:
           with async_timeout.timeout(self.rq_timeout): 
               async with session.get(urljoin(self.rq_api, "rq/queues")) as response:
                   queues = queues_from_rq(await response.text())
                   return queues


    def next_request_deferred(self):
        d = None
        if self.counter % 3==0:
            d = as_deferred(self.get_request())
        self.counter += 1
        return d

    def enqueue_request(self, request):
        print(22222, request)

    def open(self, spider):
        self.spider = spider

    def close(self, reason):
        pass

    def has_pending_requests(self):
        return True
