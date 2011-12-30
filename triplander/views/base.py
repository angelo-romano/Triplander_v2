import cherrypy
import json
from jinja2 import Environment, FileSystemLoader
from triplander import cache, settings
from triplander.views.util import map_method_to_dict

template_env = Environment(loader=FileSystemLoader('triplander/templates'))

http_renderers = {
   "text/html": (lambda inst, context: inst.template.render(context)),
   "text/plain": (lambda inst, context: inst.template.render(context)),
   "application/json": (lambda inst, context: json.dumps(context)),
}


def cherrypy_action(allowed_methods=["GET", "POST"], use_cache=False):
    """
    Decorator for all cherrypy related actions, adds more functionality
    to the simple cherrypy.expose:
    1. checks for allowed methods
    2. caching
    3. mime type customizable
    4. specific rendering by mimetype (e.g., json)
    """
    # if settings.DEBUG is True, then we allow all methods anyway
    if settings.DEBUG:
        allowed_methods = ["GET", "POST"]
        use_cache = False

    def _action(fn):
        def fn2(self, *args, **kwargs):
            # check if this method is specifically allowed here
            if cherrypy.request.method not in allowed_methods:
                cherrypy.response.headers['Allow'] = ", ".join(allowed_methods)
                raise cherrypy.HTTPError(405)

            # prepares the HTTP response and the associated renderer
            cherrypy.response.headers['Content-Type'] = self.mime_type
            renderer = http_renderers.get(self.mime_type)

            # in case of cache, checks if the context is already present
            if use_cache:
                kwarg_only = map_method_to_dict(fn, args, kwargs)
                cache_key = cache.generate_key(self.__class__.__name__,
                                               fn.__name__,
                                               kwarg_only)
            
                cached_val = cache.get(cache_key)
                if cached_val:
                    return renderer(self, cached_val)

            context = fn(self, *args, **kwargs)
            
            if use_cache:
                cache.set(cache_key, context)
            
            return renderer(self, context)
    
        return cherrypy.expose(fn2)
    return _action


class BaseView(object):
    """
    Base class definition for a cherrypy view.
    """
    template_name = None
    mime_type = "text/html"

    @property
    def template(self):
        if not self.template_name and self.mime_type == "text/html":
            raise AttributeError(
                 u"Please specify a valid template for this class")

        return template_env.get_template(self.template_name)
