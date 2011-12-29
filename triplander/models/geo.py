"""
Geo-related models.
"""
import mongokit
from pymongo.objectid import ObjectId
from triplander.mongo import settings
from triplander.mongo.base import MONGODB_CONNECTION, ModelDocument


@MONGODB_CONNECTION.register
class Country(ModelDocument):
    __collection__ = "countries"

    structure = {
        "name": unicode,
        "wikiname": unicode,
        "slug": basestring,
        "languages": [basestring],
        "currency": unicode,
        "code": basestring,
        "capital_city": ObjectId,
    }

    i18n = ['name']

    indexes = [
       {'fields': ['slug'], 'unique': True},
       {'fields': ['code'], 'unique': True},
       {'fields': ['capital_city'], 'unique': True},
    ]

    required_fields = ["name", "wikiname", "slug", "code"]


@MONGODB_CONNECTION.register
class Region(ModelDocument):
    __collection__ = "regions"

    structure = {
        "name": unicode,
        "wikiname": unicode,
        "slug": basestring,
        "languages": [basestring],
        "coordinates": [[float]],
        "countries": [ObjectId],
    }

    i18n = ['name']
    
    indexes = [
       {'fields': ['slug'], 'unique': True},
       {'fields': [('coordinates', mongokit.INDEX_GEO2D)], 'check': False},
       {'fields': ['countries']},
    ]

    required_fields = ["name", "slug"]


@MONGODB_CONNECTION.register
class City(ModelDocument):
    __collection__ = "cities"

    structure = {
        "name": unicode,
        "wikiname": unicode,
        "slug": basestring,
        "rankings": [float],
        "total_ranking": float,
        "timezone": basestring,
        "coordinates": [float],
        "country": ObjectId,
    }

    i18n = ['name']
    
    indexes = [
       {'fields': ['slug']},  # 'unique': True,
       {'fields': [('coordinates', mongokit.INDEX_GEO2D)]},
       {'fields': ['country']},
    ]
    
    required_fields = ["name", "slug"]
    default_values = {
        "total_ranking": 0.0,
        "rankings": [0.0, 0.0, 0.0],
        "timezone": "UTC+1",
        "coordinates": [0.0, 0.0],
    }
