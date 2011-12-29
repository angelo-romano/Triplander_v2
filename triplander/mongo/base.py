"""
Base classes and functions for the Mongo extension.
"""
import mongokit
from triplander.mongo import settings
from triplander.mongo.utils import get_bounding_box

MONGODB_CONNECTION = mongokit.Connection(
                         settings.MONGODB_HOST, settings.MONGODB_PORT)


class ModelDocument(mongokit.Document):
    __database__ = settings.MONGODB_DEFAULT_DATABASE
    use_schemaless = True
    use_dot_notation = True

    def find_nearby(self, field, location, distance):
        print get_bounding_box(location[0], location[1], distance)
        return self.collection.find(
            {field: {"$within":
                     {"$box": get_bounding_box(
                                   location[0], location[1], distance)}}})
