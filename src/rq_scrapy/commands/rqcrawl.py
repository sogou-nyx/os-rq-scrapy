from scrapy.commands.crawl import Command as ScrapyCommand
from scrapy.exceptions import UsageError

from rq_scrapy.crawler import CrawlerProcess


class Command(ScrapyCommand):
    default_settings = {
        "SCHEDULER": "rq_scrapy.core.scheduler.Scheduler",
        "DOWNLOADER": "rq_scrapy.core.downloader.Downloader",
        "RQ_API": "http://localhost:6789/",
        "RQ_TIMEOUT": 10,
    }

    def short_desc(self):
        return "Run a spider on rq-scrapy mode"

    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError(
                "running 'rq-scrapy rqcrawl' with more than one spider is no longer supported"
            )
        spname = args[0]

        self.crawler_process = CrawlerProcess(self.settings)
        self.crawler_process.crawl(spname, **opts.spargs)
        self.crawler_process.start()

        if self.crawler_process.bootstrap_failed:
            self.exitcode = 1
