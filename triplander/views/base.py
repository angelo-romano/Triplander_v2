from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('triplander/templates'))


class BaseView(object):
    template_name = None

    @property
    def template(self):
        if not self.template_name:
            raise AttributeError(
                 u"Please specify a valid template for this class")

        return template_env.get_template(self.template_name)
