import cherrypy
import routes


class _ctrlchain(object):

    def __init__(self, name, head=None):
        if head is None:
            self.chain = list()
        else:
            self.chain = head[:]
        self.chain.append(name)

    def __getattr__(self, attr):
        return _ctrlchain(attr, self.chain)

    def __call__(self, *args, **kwargs):
        if len(self.chain) > 3:
            raise Exception("Don't know what to do with over 3 chain elements")
        if len(self.chain) > 2:
            kwargs["action"] = self.chain[2]
        if len(self.chain) > 1:
            kwargs["controller"] = self.chain[1]

        if (len(args) == 1 and len(kwargs) == 0 and
            type(args[0]) in (str, unicode)):
            return cherrypy.url(args[0])
        else:
            return cherrypy.url(routes.url_for(*args, **kwargs))

url = _ctrlchain('urlgen')
