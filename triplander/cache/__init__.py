"""
Caching system for the application.
"""
import memcache
from triplander import settings

memcache_client = memcache.Client(['%s:%d' % (settings.MEMCACHED_HOST,
                                              settings.MEMCACHED_PORT)],
                                  debug=(1 if settings.DEBUG else 0))


def generate_key(cls_name, func_name, params={}):
    if not (func_name and isinstance(func_name, basestring)):
        raise AttributeError("Please specify a valid function name.")
    if not isinstance(params, dict):
        raise AttributeError("Please specify a valid dict of params.")

    if cls_name:
        key_name = cls_name.lower() + u'__'
    else: 
        key_name = u''

    key_name += func_name.lower()
    if params:
        key_name += u'__' + u','.join([u'%s=%s' % (k, v)
                                       for k, v in params.iteritems()])

    # keys must be always str, not unicode
    key_name = key_name.encode("utf8")

    return key_name


def get(key):
    return memcache_client.get(key)


def set(key, value):
    memcache_client.set(key, value, settings.MEMCACHED_VALIDITY_TIME)


def delete(key):
    memcache_client.delete(key)
