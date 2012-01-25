import memcache
import StringIO
import urllib2

from mwlib.dummydb import DummyDB
from mwlib.uparser import parseString
from triplander.wiki.htmlwriter import HTMLWriter

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

class WikipediaConnector(object):
    BASE_URL = "http://en.wikipedia.org/wiki/Special:Export"

    def get_page(self, name):
        request = urllib2.Request(
              "%s/Palermo" % self.BASE_URL,
              headers={
                   "User-Agent": "Mozilla/5.0 (Ubuntu; X11; Linux i686"
                                 "; rv:9.0.1) Gecko/20100101 Firefox/9.0.1"})
        
        urlopener = urllib2.urlopen(request)
        content = mc.get("wikipalermo")

        if not content:
            content = urlopener.read()
            mc.set("wikipalermo", content)
        return self._parse_wiki(content)
    
    @staticmethod
    def _parse_wiki(input):
        db = DummyDB()
    
        out = StringIO.StringIO()
    
        if input.endswith(chr(13) + chr(10)):
            input = input.replace(chr(13) + chr(10), chr(10))
        if input.endswith(chr(13)):
            input = input.replace(chr(13), chr(10))
    
        try:
            p = parseString("title", input.decode("utf8"))
        except Exception, ex:
            raise ex
            return u'Unable to parse input!'
        try:
            w = HTMLWriter(out)
        except:
            return u'Unable call HTMLWriter!'
        try:
            w.write(p)
        except Exception, ex:
            raise ex
            return u'Unable to write input!'
    
        return unicode(out.getvalue())
