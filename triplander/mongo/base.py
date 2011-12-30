"""
Base classes and functions for the Mongo extension.
"""
import mongokit
from pymongo.objectid import ObjectId
from triplander import settings
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

    @property
    def relation_set(self):
        if not getattr(self, "_relation_set", None):
            self._relation_set = ModelRelationSet(self)
        return self._relation_set 

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


class ModelRelationSet(object):
    _doc = None
    _relations = None

    def __init__(self, doc):
        self._doc = doc
        self._relations = {}
        for (relname, reltype) in getattr(self._doc, "relations", []):
            
            if (self._doc.structure.get(relname, None)
                not in (ObjectId, [ObjectId], None)):
                raise RuntimeError(u"Invalid relation name: %s" % relname)
            
            rel_obj = getattr(MONGODB_CONNECTION, reltype, None)
            if not rel_obj:
                raise RuntimeError(u"Invalid relation name: %s" % relname)

            self._relations[relname] = (relname, reltype, None)

    def __getattr__(self, name):
        try:
            val = object.__getattribute__(self, name)
        except AttributeError:
            pass
        else:
            return val
        
        # no standard attribute found, searching into relations
        val = self.fetch_relation(name)
        if not val:
            raise AttributeError(name)
        
        return val

    def fetch_relation(self, name):
        if name not in self._relations:
            return

        def getfield_attr(doc, name):
            val = getattr(doc, name, None)
            if not val:
                val = doc.get(name, None)

            return val

        relname, reltype, relobj = self._relations[name]
        
        rel_class = getattr(MONGODB_CONNECTION, reltype)
        
        rel_foreign_id = getfield_attr(self._doc, name)
        if relobj and relobj._id == rel_foreign_id:
            return relobj

        relobj = rel_class.find_one({'_id': rel_foreign_id})
        self._relations[name] = (relname, reltype, relobj)
        return relobj
