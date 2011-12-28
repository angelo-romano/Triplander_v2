"""
Root model package.
"""
from triplander.models.geo import Country
from triplander.mongo.base import MONGODB_CONNECTION

callable_set = ["Country"]

for k in callable_set:
    locals()[k] = getattr(MONGODB_CONNECTION, k)
