"""
Base classes for URL-related purposes.
"""
import sys


class SiteURL(object):
    """
    Class definition for a site URL.
    """
    def __init__(self, name, url, controller_class, action):
        self.url = url
        self.controller_class = controller_class
        self.action = action
        self.name = name
        
    def connect_to_dispatcher(self, dispatcher):
        """
        Connect this URL to a given router dispatcher.
        
        Parameters:
        dispatcher   - the dispatcher.
        """
        controller_class = self.controller_class
        if isinstance(controller_class, basestring):
            controller_class = getattr(sys.modules['triplander.views'],
                                       controller_class)

        if not issubclass(controller_class, object):
            raise AttributeError(u"Invalid controller class.")

        dispatcher.connect(self.name, self.url,
                           controller=controller_class(),
                           action=self.action)

    def __repr__(self):
        return u'<%s>' % self.__unicode__()
    
    def __unicode__(self):
        return u'SiteURL "{url}"{name}'.format(
               url=self.url,
               name=(u'' if not self.name else (u' [name=%s' % self.name)))


def convert_urls(urls):
    """
    Convert a list of tuples to SiteURLs.
    """
    for this_url in urls:
        name, url, controller_class, action = this_url

        yield SiteURL(name, url, controller_class, action)
