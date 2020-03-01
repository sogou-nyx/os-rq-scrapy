from scrapy.core.downloader import Downloader as ScrapyDownloader


class Downloader(ScrapyDownloader):
    def free_slot(self, qid):
        pass
