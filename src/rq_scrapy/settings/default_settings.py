from importlib import import_module

BOT_NAME = "rq-scrapy"

USER_AGENT = "RQ-Scrapy/%s" % import_module("rq_scrapy").__version__
