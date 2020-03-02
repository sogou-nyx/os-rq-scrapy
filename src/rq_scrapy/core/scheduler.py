import asyncio
import random
import time
import warnings

from scrapy.core.scheduler import Scheduler as ScrapyScheduler
from scrapy.utils.log import logger
from twisted.internet import defer

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
        self.async_schedule_count = 0
        self.lock = asyncio.Lock()
        self.pending_queues = set()
        self.scheduler = ScrapyScheduler.from_crawler(crawler)
        self.queues_expand = True
        self.update_queues_time = time.time()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        rq_api = settings.get("RQ_API", "http://localhost:6789/")
        rq_timeout = settings.getint("RQ_TIMEOUT", 10)
        max_concurrent = settings.getint("CONCURRENT_REQUESTS", 16)
        if max_concurrent > 500:
            warnings.warn(
                "CONCURRENT_REQUESTS > 500 is meaningless because of rq api limit, set to 500 automaticly"
            )
            max_concurrent = 500

        return cls(rq_api, rq_timeout, max_concurrent, crawler.stats, crawler)

    async def update_queues(self):
        l = len(self.pending_queues)
        if l >= self.max_concurrent:
            return
        updating = self.lock.locked()
        if (updating and l > 0) or not self._needs_update():
            return
        try:
            await self.lock.acquire()
            if not updating:
                await self.update_queues_from_rq()
        finally:
            self.lock.release()

    async def update_queues_from_rq(self):
        o = len(self.pending_queues)
        k = 2 * self.max_concurrent - o
        if k <= 0:
            return
        k = min(k, 1000)  # rq api limit
        status, ret, api_url = await queues_from_rq(
            self.rq_api, k, timeout=self.rq_timeout
        )
        if status != 200 or "queues" not in ret:
            logger.warn("Can not get queues from %s %d %s" % (api_url, status, ret))
            return

        queues = set([q["qid"] for q in ret["queues"]])
        self.pending_queues.update(queues)
        n = len(self.pending_queues)
        if n <= self.max_concurrent:
            self.queues_expand = False
        else:
            self.queues_expand = True
        self.update_queues_time = time.time()

        logger.debug(
            "Update queues from %s o=%d u=%d n=%d" % (api_url, o, len(queues), n)
        )

    async def next_queue(self):
        while True:
            await self.update_queues()
            if not self.pending_queues:
                break
            qid = random.sample(self.pending_queues, 1)[0]
            self.pending_queues.discard(qid)
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

    def _needs_update(self):
        return self.queues_expand or (time.time() - self.update_queues_time >= 1)

    async def request_from_rq(self):
        while True:
            qid = await self.next_queue()
            if not qid:
                return None
            request = await self.get_request_from_rq(qid)
            if request:
                if not self._needs_update():
                    self.pending_queues.add(qid)
                self.stats.inc_value("scheduler/dequeued/rq", spider=self.spider)
                return request

    async def next_request_from_rq(self):
        request = None
        try:
            request = await self.request_from_rq()
        except Exception as e:
            logger.error(
                "Error while getting new request from rq %s" % str(e),
                extra={"spider": self.spider},
            )
        return (request, True)

    def _async_backout(self):
        limit = min(len(self.pending_queues), self.max_concurrent)
        if limit <= 0:
            if self._needs_update():
                limit = 1
        return self.async_schedule_count >= limit

    def next_request(self):
        d = None
        if self.scheduler.has_pending_requests():
            d = defer.Deferred()
            d.callback((self.scheduler.next_request(), False))
        else:
            if not self._async_backout():
                d = as_deferred(self.next_request_from_rq())
                self.async_schedule_count += 1
        return d

    def release_request(self, request, ayc):
        if ayc:
            self.async_schedule_count -= 1

    def enqueue_request(self, request):
        return self.scheduler.enqueue_request(request)

    def open(self, spider):
        self.spider = spider
        return self.scheduler.open(spider)

    def close(self, reason):
        return self.scheduler.close(reason)

    def has_pending_requests(self):
        return True
