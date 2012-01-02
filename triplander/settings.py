"""
MongoDB host, port and all other application settings.
"""
DEBUG = True

MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DEFAULT_DATABASE = "tl2"
MEMCACHED_HOST = "127.0.0.1"
MEMCACHED_PORT = 11211
MEMCACHED_VALIDITY_TIME = 60 * 60 * 24  # 1 day

# devapp ids/api keys for external services (e.g., Google Maps, Yahoo! Travel...)
YAHOO_DEVAPP_ID = ""
GOOGLE_MAPS_API_KEY = ""
