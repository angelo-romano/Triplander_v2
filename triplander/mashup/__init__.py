# coding: latin1
import decimal
import urllib2
import urllib
import os
import re
import math
import random
from django.contrib.gis.geos import LinearRing, Polygon
from django.utils import simplejson
from xml.dom import minidom
from triplander.models import City
from triplander.remote import get_http_scheduler
from triplander.functions import getCityObject
from triplander.wiki import parse as wikiparse
#from triplander.flickr import photos_search
from triplander.models import City, Country
from triplander.settings import YAHOO_DEVAPP_ID, GOOGLEMAPS_APIKEY

def yahootravel_ranking(city_slug):
    cobj = City.find(slug=city_slug)

    query_array = cobj.name.lower().split(" ")
    if(cobj.region is not None):
        query_array.append("\"" + cobj.region.name.lower() + "\"")

    query_array.append("\"" + cobj.country.name.lower() + "\"")
    my_wikiname = re.sub(ur"[,\.:();]", " ", cobj.wikiname)
    my_wikiname = re.sub(ur" {2,}", " ", my_wikiname)
    query_array = query_array + my_wikiname.split(" ")

    yt_query = " ".join(set(query_array))

    yt_url = (("http://travel.yahooapis.com/TripService/V1.1/" + 
               "tripSearch?appid=%s&query=%s&results=%d&output=json") %
              (YAHOO_DEVAPP_ID, urllib.quote(yt_query.encode('utf-8')), 10))
    httpsched = get_http_scheduler()
    httpwhat = httpsched.urlopen(service="yahootravel", url=yt_url,
                                 json=True, alt_delta=2)

    if ('ResultSet' not in httpwhat):
        return
    if ('totalResultsAvailable' not in httpwhat['ResultSet']):
        return

    return int(httpwhat['ResultSet']['totalResultsAvailable'])
    

def yahoolocal_coordinates(city, country):
    yt_query = "%s, %s" % (city, country)
    
    # retrieve info
    yt_url = ("http://local.yahooapis.com/MapsService/V1/geocode?appid=%s&city=%s" %
              (YAHOO_DEVAPP_ID, urllib.quote(yt_query.encode('utf-8'))))
    httpsched = get_http_scheduler()
    httpwhat = httpsched.urlopen(service="yahootravel", url=yt_url,
                                 xml=True, alt_delta=2)

    # store
    xmlobj = {'latitude' : httpwhat.getElementsByTagName('Latitude'), 
              'longitude': httpwhat.getElementsByTagName('Longitude'), 
              'city'     : httpwhat.getElementsByTagName('City')}

    for k in xmlobj.keys():
        if (len(xmlobj[k]) == 0):
            return
        xmlobj[k] = xmlobj[k][0].childNodes[0].data

    # return
    return xmlobj

    
def gmaplocal_coordinates(city, country):
    yt_query = "\"%s\", \"%s\"" % (city,country)

    # retrieve info
    yt_url = ("http://maps.google.com/maps/geo?key=%s&q=%s&output=xml&hl=en-gb" %
              (GOOGLEMAPS_APIKEY, urllib.quote(yt_query.encode('utf-8'))))
    httpsched = get_http_scheduler()
    httpwhat = httpsched.urlopen(service="yahootravel", url=yt_url,
                                 xml=True, alt_delta=2)

    # check if errors were retrieved
    if (httpwhat.getElementsByTagName('code')[0].childNodes[0].data != '200'):
        return

    placemark = httpwhat.getElementsByTagName('Placemark')
    if (len(placemark) == 0):
        return

    xmlset = []
    for p in placemark:
        xmlobj = {'ranking': 1}

        # check for accuracy
        accuracy = p.getElementsByTagName('AddressDetails')
        if (len(accuracy) == 0):
            continue
        if ('Accuracy' not in accuracy[0].attributes):
            continue

        accuracy = accuracy[0].attributes['Accuracy'].value
        if (accuracy not in ('4', '5')):  # ZIP or CITY
            continue

        # locality check
        loc = p.getElementsByTagName('Locality')
        if (len(loc) == 0):
            continue

        xmlobj['ranking'] = len(loc[0].childNodes)
        if (xmlobj['ranking'] == 0):
            continue

        # coordinates    
        coords = p.getElementsByTagName('coordinates')
        if(len(coords) == 0):
            continue

        coords = coords[0].childNodes[0].data
        coords = coords.split(',')

        # locality name
        lname = p.getElementsByTagName('LocalityName')
        if (len(lname) == 0):
            continue

        lname = lname[0].childNodes[0].data

        # final return
        xmlobj.update({'latitude': coords[1], 
                       'longitude': coords[0],
                       'city': lname })
        xmlset.append(xmlobj)

    # sort by "ranking" -> official cities first, and take the best solution
    xmlset.sort(lambda x, y: x['ranking'] - y['ranking'])
    xmlobj = xmlset[0]

    # return
    return xmlobj


def delicious_popular(city_name):
    tags = city_name.split(" ")
    if ((tags is None) or (len(tags) == 0)):
        return

    tagset = "+".join(tags)    
    base_url = "http://feeds.delicious.com/v2/json/popular/%s" % tagset

    httpsched = get_http_scheduler()
    rssresp  = httpsched.urlopen(url=base_url)

    return rssresp


def panoramio_set(city_slug):
    cobj = City.find({"slug": city_slug})
    if not cobj:
        return

    panoramio_resp = _open_panoramio_conn((cobj.coordinates.x,
                                           cobj.coordinates.y))
    if (not panoramio_resp):
        return

    response = []
    for p in panoramio_resp['photos']:
        this_entry = {'href': p['photo_url'],
                      'src': p['photo_file_url'],
                      'alt': p['photo_title'],
                      }
        response.append(this_entry)
    
    return response


def panoramio_ranking(city_slug):
    cobj = City.find({"slug": city_slug})
    if not cobj:
        return
    
    panoramio_resp = _open_panoramio_conn((cobj.coordinates.x,
                                           cobj.coordinates.y), 1)
    if (not panoramio_resp):
        return 0

    return decimal.Decimal(str(panoramio_resp['count']))


def _open_panoramio_conn(coords, eps_factor=1, howmany=10):
    if not coords:
        return
    
    eps = eps_factor * 0.016  # normalization factor

    min_coordinates = (coords[0] - eps, coords[1] - eps)
    max_coordinates = (coords[0] + eps, coords[1] + eps)
    url = (("http://www.panoramio.com/map/get_panoramas.php?order=popularity"
            "&set=public&size=square&from=0&to=%d&minx=%f&miny=%f&"
            "maxx=%f&maxy=%f") %
           (howmany, min_coordinates[1], min_coordinates[0],
            max_coordinates[1], max_coordinates[0]))

    httpsched = get_http_scheduler()
    httpwhat  = httpsched.urlopen(service="panoramio", url=url, json=True)
    
    if ("photos" not in httpwhat):
        return

    return httpwhat


def weather_conditions(city_slug): # weather conditions by Google
    cobj = City.find({"slug": city_slug})
    if not cobj:
        return

    weather_url = ((u"http://www.google.com/ig/api?weather=%s,%s&hl=en-gb") %
                   (urllib.quote(cobj.name.encode('utf-8')),
                    urllib.quote(cobj.country.name.encode('utf-8'))))

    httpresp = urllib2.urlopen(weather_url)
    httpcont = httpresp.read()
    # the usual unicode mess...
    httpwhat = httpcont.replace(
                    '<?xml version="1.0"?>',
                    '<?xml version="1.0" encoding="ISO-8859-15"?>').decode(
                                                     'latin1').encode('latin1')
    
    xmlresp = minidom.parseString(httpwhat)
    success = xmlresp.getElementsByTagName('problem_cause')
    dataresp = {} 
    if len(success) == 1:
        return  # unsuccessful response (city not found)
    current_cond = xmlresp.getElementsByTagName('current_conditions')
    forecast_cond = xmlresp.getElementsByTagName('forecast_conditions')
    if (len(current_cond) == 0 or len(forecast_cond) == 0):
        return  # unsuccessful response (expected data not found)

    base_icon_url = 'http://www.google.com'
    # current conditions
    current_cond = current_cond[0]

    dataresp['current'] = {
       'temp': current_cond.getElementsByTagName(
                                     'temp_c')[0].getAttribute('data'),
       'condition': current_cond.getElementsByTagName(
                                  'condition')[0].getAttribute('data'),
       'icon': base_icon_url+current_cond.getElementsByTagName(
                                       'icon')[0].getAttribute('data'),
    }

    forecast_resp = []
    # forecast conditions
    for fc in forecast_cond:
        this_entry = {
          'temp_low': fc.getElementsByTagName(
                          'low')[0].getAttribute('data'),
          'temp_high': fc.getElementsByTagName(
                           'high')[0].getAttribute('data'),
          'condition': fc.getElementsByTagName(
                               'condition')[0].getAttribute('data'),
          'icon': base_icon_url+fc.getElementsByTagName(
                                'icon')[0].getAttribute('data'),
          'day': fc.getElementsByTagName(
                             'day_of_week')[0].getAttribute('data'),
        }
        forecast_resp.append(this_entry)

    dataresp['forecast'] = forecast_resp
    
    return dataresp


def _wikipedia_article(obj):
    dab_re = "{{disambig}}"
    #step 1: tries to access the direct page article
    httpwhat = None
    if (obj.wikiname):
        httpwhat = _open_wiki_url(obj.wikiname)
    
    if (httpwhat is None):
        httpwhat = _open_wiki_url(obj.name)

        if (httpwhat and not re.search(
                   dab_re, httpwhat['content'])):  # Apparently FOUND
            pass
        else:
            httpwhat = None
            if (obj.local_name):
                httpwhat = _open_wiki_url(obj.local_name)
            if (not httpwhat):
                query_array = []
                query_array += obj.name.split(" ")
                query_array += obj.country.name.split(" ")
                base_url = (("http://en.wikipedia.org/w/api.php?action=query"
                             "&redirects&list=search&srsearch=%s&format=json") %
                            "+".join(query_array)) 

                httpsched = get_http_scheduler()
                jsonresp = httpsched.urlopen(service="wikipedia",
                                             url=base_url.encode('utf-8'),
                                             json=True)

                if (('query' not in jsonresp) or
                    ('search' not in jsonresp['query']) or
                    (len(jsonresp['query']['search']) == 0)):
                    return
                httpwhat = _open_wiki_url(jsonresp['query']['search'][0]['title'])

    return httpwhat


def wikipedia_snippet(city_id,more='City'): # wikipedia snippet retrieval
    httpwhat = _wikipedia_article(city_id,more) # get wiki article text 
    if httpwhat is None: return None
    
    idx = httpwhat['content'].find("==",0)
    if (idx != -1): httpwhat['content']=(httpwhat['content'])[:idx]
    content = wikiparse(httpwhat['content'])
    
    # find h1/h2/h3 text
    headers = ["h1", "h2", "h3"]
    cf = lambda h: content.find("<"+h+" ")
    header_pos = [cf(h) for h in headers if (cf(h) != -1)]
    
    if(len(header_pos) > 0):
        return {'content': content[0:min(header_pos)]+"</p>", 'wikiname': httpwhat['wikiname']}
    else:
        return {'content': content, 'wikiname': httpwhat['wikiname']}

def wikipedia_ranking(name): # wikipedia ranking calculation
    rank = [decimal.Decimal("0.0"), decimal.Decimal("0.0")]
    alpha = [decimal.Decimal("0.2"), decimal.Decimal("0.8")]
    
    ops = ['recent_revisions', 'backlinks']
    
    for i in range(len(ops)):
        o = ops[i]
        json_set = _open_wiki_conn(o,name)    
        if(json_set is not None): rank[i] = len(json_set);
    
    final_rank = (alpha[0]*rank[0]+alpha[1]*rank[1])
    return {'content': final_rank, 'r1': rank[0], 'r2': rank[1]}

def city_timezone(city_id):
    city = City.objects.get(pk=city_id)
    if(city is None): return None
    
    # generate url
    tz_url = """http://www.earthtools.org/timezone/%f/%f""" % (city.coordinates.x, city.coordinates.y)
    httpsched = get_http_scheduler()
    httpwhat  = httpsched.urlopen(service="earthtools",url=tz_url,xml=True,alt_delta=1)
    
    offset_tag = httpwhat.getElementsByTagName('offset')
    if (len(offset_tag)==0): return None
    return {'offset': offset_tag[0].childNodes[0].data, 'city': city.name, 'id': city_id }

def popular_city_selection(param):
    from django.core.urlresolvers import reverse # URL reversal
    
    if (param == 'all'):
        cities = City.objects.all().order_by('-total_rating')[:30]
    else:
        param_re = re.compile("([\-0-9\.]+),([\-0-9\.]+);([\-0-9\.]+),([\-0-9\.]+)")
        re_resp  = param_re.match(param)
        if (re_resp is None): return None

        # latitude is Y - longitude is X
        latlong1  = (float(re_resp.group(1)),float(re_resp.group(2)))
        latlong2  = (float(re_resp.group(3)),float(re_resp.group(4)))
        
        # get cities within a given rectangle range - build filtering object
        lr = Polygon(LinearRing( # latitude is Y - longitude is X
                        latlong1,  # SW Corner
                        (latlong1[0],latlong2[1]),
                        latlong2,  # NE Corner
                        (latlong2[0],latlong1[1]),
                        latlong1,  # SW Corner 
                        ))
    
        cities = City.objects.filter(coordinates__within=lr).order_by('-total_rating')[:30]

    #city_selection = random.sample(xrange(len(cities)),50)
    
    return [{'id'  : c.id, 
             'url' : reverse('city_by_id',args=[c.id,c.slug]),
             'name': c.name, 
             'x'   : c.coordinates.x, 
             'y'   : c.coordinates.y} for c in cities]

def commons_image(country_id):
    cobj = Country.objects.get(id=country_id)
    if(cobj is None): return None
    
    correct_name = "".join([w.capitalize() for w in cobj.name.split(" ")])
    width = 300
    #imgname = "Location%s.svg" % correct_name
    imghref = """http://commons.wikimedia.org/wiki/Image:%s""" % (cobj.map)
    #s = _open_commons_image(imgname,width=300)
    s = {'src' : cobj.getMapURL(),
         'href': imghref,
         'alt' : cobj.name + " map"
         }
    return s

def _open_wiki_conn(op,name):
    wikiurls = {
                "current_revision": u"http://en.wikipedia.org/w/api.php?action=query&redirects&prop=revisions&titles=%s&rvprop=content&format=json", 
                "recent_revisions": u"http://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=%s&rvlimit=500&rvprop=user|flags&rvdir=newer&rvstart=%s&format=json",
                "backlinks"       : u"http://en.wikipedia.org/w/api.php?action=query&list=backlinks&bltitle=%s&bllimit=500&blnamespace=0&blfilterredir=nonredirects&format=json",
               }
    
    if (not wikiurls.has_key(op)): return None
    wiki_base_url = wikiurls[op]
    if(op == 'recent_revisions'):
        tstamp = '20081001000000'
        wiki_url = wiki_base_url % (name.replace(" ","_"),tstamp)
    else:
        wiki_url = wiki_base_url % name.replace(" ","_")

    httpsched = get_http_scheduler()
    httpwhat  = httpsched.urlopen(service="wikipedia",url=wiki_url.encode('utf-8'),json=True)
    
    if (not httpwhat.has_key('query')): return None
    if(op == 'backlinks'):
        if (not httpwhat['query'].has_key('backlinks')): return None
        json_set = httpwhat['query']['backlinks']
    else:
        if (not httpwhat['query'].has_key('pages')): return None
        json_set = httpwhat['query']['pages']
        if (json_set.keys()[0] == '-1'): return None
        if (not json_set.values()[0].has_key('revisions')): return None
        if (op == 'recent_revisions'):
            return json_set.values()[0]['revisions']
        else:
            return json_set.values()[0]

    return json_set
   
def _open_wiki_url(name):
    json_set = _open_wiki_conn('current_revision',name)
    if(json_set is None): return None
    wikiname = json_set['title'].replace(" ","_")
    
    return {'content': json_set['revisions'][0]['*'], 'wikiname': wikiname}

def _open_commons_image(image,width=450):
    resp = { 'src': None, 'href': None, 'width': None, 'height': None}
    url = """http://toolserver.org/~magnus/commonsapi.php?image=%s&thumbwidth=%d&languages=en""" % (urllib.quote(image.encode('utf-8')),width)
    
    httpsched = get_http_scheduler()
    xmlresp   = httpsched.urlopen(service="commons",url=url,xml=False)
    return xmlresp
    if (xmlresp is None): return None
    # see http://toolserver.org/~magnus/commonsapi.php for details
    try:
        filedesc = xmlresp.getElementsByTagName('response')
        filedesc = filedesc[0].getElementsByTagName('file')
        
        urldesc  = filedesc[0].getElementsByTagName('urls')
        
        resp['href'] = urldesc.getElementsByTagName('description')[0].firstChild.nodeValue
        resp['src']  = urldesc.getElementsByTagName('thumbnail')[0].firstChild.nodeValue
        
        resp['width']= filedesc.getElementsByTagName('width')[0].firstChild.nodeValue
        resp['height']= filedesc.getElementsByTagName('height')[0].firstChild.nodeValue
    except:
        resp = None
        
    return resp
