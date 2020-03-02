import pathlib

import rq_scrapy


def test_version():
    version_file = (
        pathlib.Path(__file__).parents[1].joinpath("src/rq_scrapy/VERSION").absolute()
    )
    assert rq_scrapy.__version__ == open(version_file).read().strip()


if __name__ == "__main__":
    test_version()
