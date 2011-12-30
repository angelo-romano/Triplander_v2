"""
Site configuration for URLs. 
"""
from triplander.urls.base import convert_urls
site_urls = (
    (u'home', u'/', u'Root', u'index'),
    (u'city', u'/city/{slug}', u'CityView', u'get_by_slug'),
    (u'by_prefix', u'/ajax/{obj}/by_prefix/{prefix}',
     u'AJAXSearchView', u'get_by_prefix'),
    (u'by_coordinates', u'/ajax/{obj}/by_coordinates/{latlng}',
     u'AJAXSearchView', u'get_by_coordinates'),
)

site_urls = convert_urls(site_urls)