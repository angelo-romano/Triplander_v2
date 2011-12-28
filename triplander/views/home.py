from triplander.views.base import BaseView
import cherrypy


class Root(BaseView):
    """
    Root node - homepage
    """
    template_name = "index.html"

    @cherrypy.expose
    def index(self):
        return self.template.render(salutation='Hello', target='World')


class CityView(BaseView):
    template_name = "city.html"

    @cherrypy.expose
    def get_by_slug(self, slug):
        return self.template.render(slug=slug)
