"""
Base classes and functions for the Mongo extension.
"""
import mongokit
from triplander.mongo import settings
from triplander.mongo.util import get_bounding_box

MONGODB_CONNECTION = mongokit.Connection(
                         settings.MONGODB_HOST, settings.MONGODB_PORT)


class ModelDocument(mongokit.Document):
    """
    A enhanced version of mongokit.Document for our purposes.
    """
    __database__ = settings.MONGODB_DEFAULT_DATABASE
    use_schemaless = True
    use_dot_notation = True

    def find_nearby(self, field, location, distance):
        """
        Find objects located in a given distance from a specific location.

        Parameters:
        field      (basestring) - a field name, referring to some coordinates.
        location   (list/tuple) - a 2-list/tuple (latitude, longitude).
        distance   (float)      - the distance in km.
        """
        return self.find(
            {field: {"$within":
                     {"$box": get_bounding_box(
                                   location[0], location[1], distance)}}})

    def find_prefix(self, field, prefix):
        """
        Find objects whose field value start with a given prefix.

        Parameters:
        field      (basestring) - a field name (can be localized too).
        prefix     (basestring) - a prefix (string).
        """
        if field in self.i18n:
            field += ".value"

        return self.find({field: {"$regex": "^%s" % prefix,
                                  "$options": "i"}})
