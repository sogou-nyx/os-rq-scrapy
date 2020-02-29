from scrapy.core.engine import ExecutionEngine
from scrapy.utils.log import failure_to_exc_info, logger
from twisted.internet import defer


class Engine(ExecutionEngine):
    @defer.inlineCallbacks
    def open_spider(self, spider, start_requests=(), close_if_idle=False):
        yield super(Engine, self).open_spider(spider, start_requests, close_if_idle)

    def _scrapy_next_request_from_scheduler(self, request, spider):
        slot = self.slot
        if not request:
            slot.scheduler.incr_active_request(-1)
            return
        d = self._download(request, spider)
        d.addBoth(self._handle_downloader_output, request, spider)
        d.addErrback(
            lambda f: logger.info(
                "Error while handling downloader output",
                exc_info=failure_to_exc_info(f),
                extra={"spider": spider},
            )
        )
        d.addBoth(lambda _: slot.remove_request(request))
        d.addBoth(lambda _: slot.scheduler.incr_active_request(-1))
        d.addErrback(
            lambda f: logger.info(
                "Error while removing request from slot",
                exc_info=failure_to_exc_info(f),
                extra={"spider": spider},
            )
        )
        d.addBoth(lambda _: slot.nextcall.schedule())
        d.addErrback(
            lambda f: logger.info(
                "Error while scheduling new request",
                exc_info=failure_to_exc_info(f),
                extra={"spider": spider},
            )
        )
        return d

    def _next_request_from_scheduler(self, spider):
        slot = self.slot
        d = slot.scheduler.next_request_deferred()
        if not d:
            return
        d.addCallback(self._scrapy_next_request_from_scheduler, spider)
        d.addErrback(
            lambda f: logger.info(
                "Error while scheduing new request from rq",
                exc_info=failure_to_exc_info(f),
                extra={"spider": spider},
            )
        )
        return d
