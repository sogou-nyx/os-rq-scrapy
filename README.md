# os-rq-scrapy

[![Build Status](https://www.travis-ci.org/cfhamlet/os-rq-scrapy.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-rq-scrapy)
[![codecov](https://codecov.io/gh/cfhamlet/os-rq-scrapy/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-rq-scrapy)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/os-rq-scrapy.svg)](https://pypi.python.org/pypi/os-rq-scrapy)
[![PyPI](https://img.shields.io/pypi/v/os-rq-scrapy.svg)](https://pypi.python.org/pypi/os-rq-scrapy)


A framework for [Scrapy](https://github.com/scrapy/scrapy) working with [os-go-rq](https://github.com/cfhamlet/os-go-rq) to build "broad crawls" system.

As you know, Scrapy is a very popular python crawler framework. It is suit for "focused crawl": start from several URLs of specific sites, fetch html, extract and save "structured data" also with patternd links to crawl recursively. But for large scale, long time crawling especially ["broad crawls" ](https://docs.scrapy.org/en/latest/topics/broad-crawls.html), scrapy is not incompetent. Basically, you have to decouple the whole crawling system into several sub-systems, high-performance distributed fetcher, task scheduler, html extractor, link database, data storage and a lot of auxiliary equipments. It will be more complex when your system is for multi-tenancy.

The os-rq-scrapy and [os-go-rq](https://github.com/cfhamlet/os-go-rq) project are basic components to build "broad crawls" system. The core conceptions are very simple, os-go-rq is multi-sites request queue have http api to recieve requests. os-rq-scrapy is fetcher, getting reqests from os-go-rq and crawl multi-sites concurrently. 


## Requirements

* Python 3.6+ (pypy3.6+)
* [Scrapy](https://github.com/scrapy/scrapy) 1.8.0+

extra requirements:

* [ujson](https://github.com/ultrajson/ultrajson), for json performance

## Install

```
pip install os-rq-scrapy
```

## Usage

### Command line

``rq-scrapy`` command enhance the basic ``scrapy`` command. When RQ_API is configured, the ``crawl`` subcommand will run on rq mode, get requests from rq.

## Unit Tests

```
tox
```

## License

MIT licensed.
