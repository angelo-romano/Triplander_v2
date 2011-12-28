"""
Root view package.
"""
import cherrypy
import os
from triplander.views.home import Root, CityView


def setup_routes():
    d = cherrypy.dispatch.RoutesDispatcher()
    d.connect('home', '/', controller=Root(), action='index')
    d.connect(None, '/city/{slug}', controller=CityView(), action='get_by_slug')
    dispatcher = d
    return dispatcher

urlconf = {
    '/': {
        'request.dispatch': setup_routes()
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.dir': 'static'
    }
}

__all__ = ['urlconf']
