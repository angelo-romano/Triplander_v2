"""
Base classes and functions for the Mongo extension.
"""
import mongokit
from triplander.mongo import settings

MONGODB_CONNECTION = mongokit.Connection(
                         settings.MONGODB_HOST, settings.MONGODB_PORT)


class ModelDocument(mongokit.Document):
    __database__ = settings.MONGODB_DEFAULT_DATABASE
    use_schemaless = True
    use_dot_notation = True
