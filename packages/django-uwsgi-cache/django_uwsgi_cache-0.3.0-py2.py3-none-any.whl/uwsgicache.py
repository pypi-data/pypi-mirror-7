"""uWSGI cache backend"""
__version__ = "0.3.0"

try:
    from django.utils.encoding import force_bytes as stringify
except ImportError:
    from django.utils.encoding import smart_str as stringify
from django.core.cache.backends.base import BaseCache, InvalidCacheBackendError
from django.conf import settings

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import uwsgi
except ImportError:
    if getattr(settings, "UWSGI_CACHE_FALLBACK", True):
        uwsgi = None
    else:
        raise InvalidCacheBackendError(
            "You're not running under uWSGI ! "
            "Set UWSGI_CACHE_FALLBACK=True in settings if you want to fallback "
            "to LocMemCache."
        )


if uwsgi:
    class UWSGICache(BaseCache):
        def __init__(self, server, params):
            BaseCache.__init__(self, params)
            self._cache = uwsgi
            self._server = server

        def exists(self, key):
            return self._cache.cache_exists(stringify(key), self._server)

        def add(self, key, value, timeout=None, version=None):
            if timeout is None:
                timeout = self.default_timeout
            key = self.make_key(key, version=version)
            if self.exists(key):
                return False
            return self.set(key, value, timeout, self._server)

        def get(self, key, default=None, version=None):
            key = self.make_key(key, version=version)
            val = self._cache.cache_get(stringify(key), self._server)
            if val is None:
                return default
            val = stringify(val)
            return pickle.loads(val)

        def set(self, key, value, timeout=None, version=None):
            if timeout is None:
                timeout = self.default_timeout
            key = self.make_key(key, version=version)
            self._cache.cache_update(stringify(key), pickle.dumps(value), timeout, self._server)

        def delete(self, key, version=None):
            key = self.make_key(key, version=version)
            self._cache.cache_del(stringify(key), self._server)

        def close(self, **kwargs):
            pass

        def clear(self):
            self._cache.cache_clear(self._server)
else:
    from django.core.cache.backends.locmem import LocMemCache as UWSGICache # flake8: noqa
