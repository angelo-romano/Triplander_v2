import cherrypy
from triplander.views import urlconf

cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(None, config=urlconf)
