import six
from scrapy.crawler import (
    Crawler as ScrapyCrawler,
    CrawlerProcess as ScrapyCrawlerProcess,
)

from rq_scrapy.core.engine import Engine


class Crawler(ScrapyCrawler):
    def _create_engine(self):
        return Engine(self, lambda _: self.stop())


class CrawlerProcess(ScrapyCrawlerProcess):
    def _create_crawler(self, spidercls):
        if isinstance(spidercls, six.string_types):
            spidercls = self.spider_loader.load(spidercls)
        return Crawler(spidercls, self.settings)
