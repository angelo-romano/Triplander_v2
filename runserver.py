import cherrypy
from triplander.views import urlconf

app = cherrypy.tree.mount(None, config=urlconf)

cherrypy.quickstart(app)
