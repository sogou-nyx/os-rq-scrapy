from os.path import join

from scrapy.commands.startproject import Command as ScrapyCommand

import rq_scrapy


class Command(ScrapyCommand):
    def short_desc(self):
        return "Create new rq-scrapy project"

    @property
    def templates_dir(self):
        _templates_base_dir = self.settings["TEMPLATES_DIR"] or join(
            rq_scrapy.__path__[0], "templates"
        )
        return join(_templates_base_dir, "project")
