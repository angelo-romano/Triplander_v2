"""
Root view package.
"""
import cherrypy
import os
import triplander
from triplander.views.home import Root, CityView, AJAXSearchView
from triplander.urls import site_urls

def setup_routes():
    d = cherrypy.dispatch.RoutesDispatcher()
    for this_url in site_urls:
        this_url.connect_to_dispatcher(d)

    dispatcher = d
    return dispatcher

urlconf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    },
    '/': {
        'request.dispatch': setup_routes(),
    },
    '/media': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': os.path.dirname(os.path.abspath(triplander.__file__)),
        'tools.staticdir.dir': 'media',
    }
}

__all__ = ['urlconf', 'Root', 'CityView', 'AJAXSearchView']
