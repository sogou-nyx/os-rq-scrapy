from importlib import import_module
from os.path import abspath, dirname, join

BOT_NAME = "rq-scrapy"

TEMPLATES_DIR = abspath(join(dirname(__file__), "..", "templates"))

USER_AGENT = "RQ-Scrapy/%s" % import_module("rq_scrapy").__version__

RQ_API = "http://localhost:6789/"

RQ_TIMEOUT = 10
