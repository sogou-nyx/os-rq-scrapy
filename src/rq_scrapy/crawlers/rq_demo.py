from scrapy.crawler import Crawler as ScrapyCrawler
from scrapy.settings import Settings

from rq_scrapy.cores.rq_demo.engine import Engine

default_settings = {
    "SCHEDULER": "rq_scrapy.cores.rq_demo.scheduler.Scheduler",
    "DOWNLOADER": "rq_scrapy.cores.rq_demo.downloader.Downloader",
    "RQ_TIMEOUT": 10,
}


class Crawler(ScrapyCrawler):
    name = "rq-demo"

    def __init__(self, spidercls, settings=None):
        if isinstance(settings, dict) or settings is None:
            settings = Settings(settings)
        settings.setdict(default_settings, "default")
        super(Crawler, self).__init__(spidercls, settings)

    def _create_engine(self):
        return Engine(self, lambda _: self.stop())
