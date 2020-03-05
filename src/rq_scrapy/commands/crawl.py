from scrapy.commands.crawl import Command as ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.log import logger

from rq_scrapy.crawlers import get_crawlers_dict, load_crawler_class


class Command(ScrapyCommand):
    def add_options(self, parser):
        super(Command, self).add_options(parser)
        self.crawlers = get_crawlers_dict("rq_scrapy.crawlers")
        parser.add_option(
            "-c",
            "--crawler-class",
            metavar="CRAWLER_CLASS",
            help=(
                "set crawler class. "
                "choose from %r "
                "default 'scrapy' if RQ_API is not configured. "
                "crawler class path is also acceptable"
            )
            % list(self.crawlers),
        )
        parser.add_option(
            "-r",
            "--rq-api",
            metavar="RQ_API",
            help=("set rq api uri. " "the default crawler class will be 'rq-demo'"),
        )

    def process_options(self, args, opts):
        super(Command, self).process_options(args, opts)
        self.settings.set("CRAWLER_CLASS", "scrapy", "command")
        if opts.crawler_class:
            self.settings.set("CRAWLER_CLASS", opts.crawler_class, "cmdline")
        if opts.rq_api:
            self.settings.set("RQ_API", opts.rq_api, "cmdline")

        if self.settings.get("RQ_API", None):
            self.settings.set("CRAWLER_CLASS", "rq-demo", "command")
            self.settings.set(
                "TWISTED_REACTOR",
                "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
                "command",
            )

    def _create_crawler(self, spname):
        c = self.settings.get("CRAWLER_CLASS")
        crawler_class = None
        if c in self.crawlers:
            crawler_class = self.crawlers[c]
        else:
            crawler_class = load_crawler_class(c)
        return crawler_class(
            self.crawler_process.spider_loader.load(spname), self.settings
        )

    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError(
                (
                    "running 'rq-scrapy crawl' ",
                    "with more than one spider is no longer supported",
                )
            )
        spname = args[0]

        crawler = self._create_crawler(spname)
        logger.debug("Crawler %s.%s" % (crawler.__module__, crawler.__class__.__name__))

        crawl_defer = self.crawler_process.crawl(crawler, **opts.spargs)

        if getattr(crawl_defer, "result", None) is not None and issubclass(
            crawl_defer.result.type, Exception
        ):
            self.exitcode = 1
        else:
            self.crawler_process.start()

            if self.crawler_process.bootstrap_failed or (
                hasattr(self.crawler_process, "has_exception")
                and self.crawler_process.has_exception
            ):
                self.exitcode = 1
