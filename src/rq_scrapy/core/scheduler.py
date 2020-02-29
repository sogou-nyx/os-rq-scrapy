import asyncio
import random

from scrapy.utils.log import logger

from rq_scrapy.utils.asyncio_defer import as_deferred
from rq_scrapy.utils.rqdata import queues_from_rq, request_from_rq


class Scheduler(object):
    def __init__(
        self, rq_api, rq_timeout=10, max_concurrent=16, stats=None, crawler=None
    ):
        self.rq_api = rq_api
        self.rq_timeout = rq_timeout
        self.crawler = crawler
        self.stats = stats
        self.max_concurrent = max_concurrent
        self.active_request_count = 0
        self.lock = asyncio.Lock()
        self.queues = set()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        rq_api = settings.get("RQ_API", "http://localhost:6789/")
        rq_timeout = settings.getint("RQ_TIMEOUT", 10)
        max_concurrent = settings.getint("CONCURRENT_REQUESTS", 16)
        return cls(rq_api, rq_timeout, max_concurrent, crawler.stats, crawler)

    async def update_queues(self):
        if len(self.queues) >= self.max_concurrent:
            return
        updated = self.lock.locked()
        if updated and len(self.queues) > 0:
            return
        try:
            await self.lock.acquire()
            if not updated:
                await self.update_queues_from_rq()
        finally:
            self.lock.release()

    async def update_queues_from_rq(self):
        k = 2 * self.max_concurrent - len(self.queues)
        if k <= 0:
            return
        status, ret, api_url = await queues_from_rq(
            self.rq_api, k, timeout=self.rq_timeout
        )
        if status != 200 or "queues" not in ret:
            logger.warn("Can not get queues from %s %d %s" % (api_url, status, ret))
            return

        queues = set([q["qid"] for q in ret["queues"]])
        self.queues.update(queues)
        logger.debug(
            "Update queues from %s %d %d" % (api_url, len(queues), len(self.queues))
        )

    async def next_queue(self):
        while True:
            await self.update_queues()
            if not self.queues:
                break
            qid = random.sample(self.queues, 1)[0]
            self.queues.discard(qid)
            return qid

    async def get_request_from_rq(self, qid):
        status, ret, api_url = await request_from_rq(
            self.rq_api, qid, timeout=self.rq_timeout
        )
        if status != 200:
            logger.warn("Can not get request from %s %d %s" % (api_url, status, ret))
            return None
        logger.debug("Get request from %s %s" % (api_url, str(ret)))
        return ret

    async def _get_request(self):
        while True:
            qid = await self.next_queue()
            if not qid:
                return None
            request = await self.get_request_from_rq(qid)
            if request:
                return request

    async def get_request(self):
        try:
            return await self._get_request()
        except Exception as e:
            logger.error(
                "Error while getting new request from rq %s" % str(e),
                extra={"spider": self.spider},
            )

    def next_request_deferred(self):
        if self.active_request_count >= self.max_concurrent:
            return None
        self.incr_active_request(1)
        d = as_deferred(self.get_request())
        return d

    def incr_active_request(self, d):
        self.active_request_count += d

    def enqueue_request(self, request):
        print(22222, request)

    def open(self, spider):
        self.spider = spider

    def close(self, reason):
        pass

    def has_pending_requests(self):
        return True
