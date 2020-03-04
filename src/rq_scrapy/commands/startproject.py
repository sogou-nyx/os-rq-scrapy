from os.path import abspath, dirname, join

from scrapy.commands.startproject import Command as ScrapyCommand


class Command(ScrapyCommand):
    default_settings = {
        "LOG_ENABLED": False,
        "SPIDER_LOADER_WARN_ONLY": True,
        "TEMPLATES_DIR": abspath(join(dirname(__file__), "..", "templates")),
    }

    def short_desc(self):
        return "Create new rq-scrapy project"

    def run(self, args, opts):
        if len(args) not in (1, 2):
            raise UsageError()

        project_name = args[0]
        project_dir = args[0]

        if len(args) == 2:
            project_dir = args[1]

        if exists(join(project_dir, "scrapy.cfg")):
            self.exitcode = 1
            print("Error: scrapy.cfg already exists in %s" % abspath(project_dir))
            return

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        self._copytree(self.templates_dir, abspath(project_dir))
        move(join(project_dir, "module"), join(project_dir, project_name))
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(
                project_dir, string.Template(path).substitute(project_name=project_name)
            )
            render_templatefile(
                tplfile,
                project_name=project_name,
                ProjectName=string_camelcase(project_name),
            )
        print(
            "New RQ-Scrapy project '%s', using template directory '%s', "
            "created in:" % (project_name, self.templates_dir)
        )
        print("    %s\n" % abspath(project_dir))
        print("You can start your first spider with:")
        print("    cd %s" % project_dir)
        print("    rq-scrapy genspider example example.com")
