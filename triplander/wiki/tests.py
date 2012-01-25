import memcache
from triplander.remote import WikipediaConnector

def test_getpage():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    page = WikipediaConnector().get_page("Palermo")

    print page