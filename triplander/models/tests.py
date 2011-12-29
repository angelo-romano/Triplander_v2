from triplander.models import City

city = City.find_one({"slug": "groningen"})
point = city.coordinates
distance = 20

City.set_lang("en")
for c in City.find_nearby("coordinates", point, distance):
    print "1", c.name

for c in City.find_prefix("name", "gro"):
    print "2", c.name
