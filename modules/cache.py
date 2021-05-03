# encoding: utf-8
# storage = "memcached://10.0.3.136/?ttl=120"
# storage = "redis://:master@10.0.3.136/1?ttl=120"

import redis
from urllib.parse import urlparse, parse_qs
from modules.settings import get_setting
from fastapi import HTTPException


class InvalidCacheException(HTTPException):
    def __init__(self, client):
        super(InvalidCacheException, self).__init__(detail=f'Unknown client {client}', status_code=500)


class ConnectionException(HTTPException):
    def __init__(self):
        super(ConnectionException, self).__init__(detail=f'cache error', status_code=500)


PREFIX = 'bucket_'


class BaseClient(object):
    def __init__(self, url):
        if url:
            self.query = parse_qs(url.query)
            self.host = url.hostname

    def set(self, key, value, ttl=None):
        pass

    def get(self, key):
        return None

    def delete_by_pattern(self, pattern):
        return 0


class NullClient(BaseClient):
    pass


class RedisClient(BaseClient):

    def __init__(self, url):
        super().__init__(url)
        self.port = 6379 if url.port is None else url.port
        self.ttl = int(self.query.get("ttl", [120])[0])
        self.password = url.password

        self.db = 1
        try:
            self.db = int(url.path[1:])
        except Exception:
            raise ConnectionException()
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.password)

    def set(self, key, value, ttl=None):
        ttl = ttl if ttl else self.ttl
        k = PREFIX + key
        self.r.set(k, value, ex=ttl)

    def get(self, key):
        try:
            k = PREFIX + key
            return self.r.get(k)
        except Exception:
            raise ConnectionException()

    def delete_by_pattern(self, pattern):
        keys = self.r.keys(PREFIX + pattern)
        if not keys:
            return 0
        return self.r.delete(*keys)


CACHE_CLIENTS = {
    "redis": RedisClient
}


def get_cache_client():
    config_cache = get_setting().cache_uri
    if config_cache is None:
        return NullClient(config_cache)
    url_parsed = urlparse(config_cache)
    cache_class = CACHE_CLIENTS.get(url_parsed.scheme)
    if cache_class is None:
        raise InvalidCacheException(url_parsed.scheme)
    client = cache_class(url_parsed)
    return client


