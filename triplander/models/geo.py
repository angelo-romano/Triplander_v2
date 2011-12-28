"""
Geo-related models.
"""
from triplander.mongo import settings
from triplander.mongo.base import MONGODB_CONNECTION, ModelDocument


@MONGODB_CONNECTION.register
class Country(ModelDocument):
    __collection__ = "countries"
    __database__ = settings.MONGODB_DEFAULT_DATABASE

    structure = {
        "name": unicode,
        "local_names": {basestring: unicode},
        "wikiname": unicode,
        "slug": basestring,
        "languages": [basestring],
        "currency": unicode,
        "code": basestring,
    }
    
    required_fields = ["name", "wikiname", "slug", "code"]


@MONGODB_CONNECTION.register
class Region(ModelDocument):
    __collection__ = "regions"
    __database__ = settings.MONGODB_DEFAULT_DATABASE

    structure = {
        "name": unicode,
        "local_names": {basestring: unicode},
        "wikiname": unicode,
        "slug": basestring,
        "languages": [basestring],
        "coordinates": [[float]],
        "code": basestring,
    }
    
    required_fields = ["name", "slug"]


@MONGODB_CONNECTION.register
class City(ModelDocument):
    __collection__ = "cities"
    __database__ = settings.MONGODB_DEFAULT_DATABASE

    structure = {
        "name": unicode,
        "local_names": {basestring: unicode},
        "alternate_names": [unicode],
        "wikiname": unicode,
        "slug": basestring,
        "rankings": [float],
        "total_ranking": float,
        "timezone": basestring,
        "coordinates": [float],
    }
    
    required_fields = ["name", "wikiname", "slug", "code"]
    default_values = {
        "total_ranking": 0.0,
        "rankings": [0.0, 0.0, 0.0],
        "timezone": "UTC+1",
        "coordinates": [0.0, 0.0],
        "alternate_names": [],
    }
