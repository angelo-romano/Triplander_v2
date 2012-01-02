from triplander.models import City, Country
from triplander.mongo.util import get_distance
from triplander.views.base import BaseView, cherrypy_action
import cherrypy


class Root(BaseView):
    """
    Root node - homepage
    """
    template_name = "index.html"

    @cherrypy_action()
    def index(self):
        return dict(salutation='Hello', target='World')


class CityView(BaseView):
    template_name = "city.html"

    @cherrypy_action()
    def get_by_slug(self, slug):
        city = City.find_one({"slug": slug})
        country = city.relation_set.country
        return {
            "city": city,
            "country": country,
        }


class AJAXSearchView(BaseView):
    mime_type = "application/json"

    def _get_cities_by_prefix(self, prefix):
        for city in City.find_prefix('name', prefix):
            yield {"name": city.name,
                   "slug": city.slug,
                   "country_code": city.relation_set.country.code.lower()}

    def _get_countries_by_prefix(self, prefix):
        for country in Country.find_prefix('name', prefix):
            yield {"name": country.name,
                   "slug": country.slug,
                   "capital_city": country.relation_set.capital_city.name}

    @cherrypy_action(allowed_methods=["POST"], use_cache=True)
    def get_by_prefix(self, obj, prefix):
        if obj == "city":
            entries = self._get_cities_by_prefix(prefix)
        elif obj == "country":
            entries = self._get_countries_by_prefix(prefix)
        
        return sorted(entries,
                      key=lambda k: k["name"])

    @cherrypy_action(allowed_methods=["POST"], use_cache=True)
    def get_by_coordinates(self, obj, latlng):
        lat, lng = map(float, latlng.split(";"))
        resp = []
        for city in City.find_nearby('coordinates', [lat, lng], 100):
            resp.append({"name": city.name,
                         "slug": city.slug,
                         "country": city.relation_set.country.name,
                         "distance": get_distance([lat, lng],
                                                  city.coordinates)})

        return sorted(resp, key=lambda k: k["distance"])
