"""
Root model package.
"""
from triplander.models.geo import Country, Region, City
from triplander.mongo.base import MONGODB_CONNECTION

callable_set = ["Country", "City", "Region"]

for k in callable_set:
    locals()[k] = getattr(MONGODB_CONNECTION, k)
