from scrapy.core.engine import ExecutionEngine
from scrapy.utils.log import failure_to_exc_info, logger
from twisted.internet import defer


class Engine(ExecutionEngine):
    def __init__(self, crawler, spider_closed_callback):
        super(Engine, self).__init__(crawler, spider_closed_callback)
        self.total_concurrency = self.crawler.settings.getint("CONCURRENT_REQUESTS")
        self.scheduling = set()

    @defer.inlineCallbacks
    def open_spider(self, spider, start_requests=(), close_if_idle=False):
        yield super(Engine, self).open_spider(spider, start_requests, close_if_idle)

    def _next_request_from_scheduler(self, spider):
        slot = self.slot
        d = slot.scheduler.next_request()
        if not d:
            return
        self.scheduling.add(d)
        d.addCallback(super(Engine, self)._next_request_from_scheduler, spider)
        d.addBoth(lambda _: self.scheduling.discard(d))
        d.addErrback(
            lambda f: logger.info(
                "Error while scheduing new deferred request",
                exc_info=failure_to_exc_info(f),
                extra={"spider": spider},
            )
        )
        return d

    def _needs_backout(self, spider):
        return (
            super(Engine, self)._needs_backout(spider)
            or len(self.scheduling) >= self.total_concurrency
        )
