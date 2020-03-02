from scrapy.commands.crawl import Command as ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.log import logger

from rq_scrapy.crawler import CrawlerProcess


class Command(ScrapyCommand):
    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.add_option("-r", "--rq-api", metavar="RQ-API", help="set rq-api")

    def process_options(self, args, opts):
        super(Command, self).process_options(args, opts)
        if opts.rq_api or self.settings.get("RQ_API", None):
            self.settings.setdict(
                {
                    "SCHEDULER": "rq_scrapy.core.scheduler.Scheduler",
                    "DOWNLOADER": "rq_scrapy.core.downloader.Downloader",
                    "REACTOR_THREADPOOL_MAXSIZE": 20,
                    "RQ_TIMEOUT": 10,
                },
                "command",
            )
            if opts.rq_api:
                settings.set("RQ_API", opts.rq_api, priority="cmdline")

    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError(
                "running 'rq-scrapy crawl' with more than one spider is no longer supported"
            )
        spname = args[0]

        if self.settings.get("RQ_API", None):
            self.crawler_process = CrawlerProcess(self.settings)
            logger.info("Run on rq mode")
        else:
            logger.info("Run on scrapy mode")
        self.crawler_process.crawl(spname, **opts.spargs)
        self.crawler_process.start()

        if self.crawler_process.bootstrap_failed:
            self.exitcode = 1
