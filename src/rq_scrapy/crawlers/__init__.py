import inspect

from scrapy.crawler import Crawler
from scrapy.utils.misc import load_object, walk_modules


class ScrapyCrawler(Crawler):
    name = "scrapy"


def _is_crawler_class(obj):
    return inspect.isclass(obj) and issubclass(obj, Crawler) and not obj == Crawler


def load_crawler_class(class_path):
    obj = load_object(class_path)
    if _is_crawler_class(obj):
        return obj


def _iter_crawler_classes(module_name):
    for module in walk_modules(module_name):
        for obj in vars(module).values():
            if _is_crawler_class(obj):
                yield obj


def get_crawlers_dict(module):
    d = {}
    for mode in _iter_crawler_classes(module):
        name = mode.__module__.split(".")[-1].replace("_", "-")
        if hasattr(mode, "name"):
            name = mode.name
        d[name] = mode
    return d
