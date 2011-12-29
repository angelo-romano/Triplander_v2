from triplander.models import City

city = City.find_one({"slug": "groningen"})
point = city.coordinates
distance = 20

for c in City.find_nearby("coordinates", point, distance):
    print c
