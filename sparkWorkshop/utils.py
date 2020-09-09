import re
from functools import wraps

import phonenumbers as pn
import pytz
import requests
from django.conf import settings
from django.core.cache import caches
from django.utils.encoding import smart_str
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse

# Default values for cache
DEFAULT_CACHE_ALIAS = 'default'
DEFAULT_CACHE_TIME = 60 * 30  # 30 minutes


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def _smart_key(key):
    return smart_str(
        ''.join([c for c in key if ord(c) > 32 and ord(c) != 127])
    )


def make_key(key, key_prefix, version):
    """
    Truncate all keys to 250 or less and remove control characters, for using
    with memcached
    """
    return ':'.join([key_prefix, str(version), _smart_key(key)])[:250]

    def cache_return_wrapper(f=None, cache_time=DEFAULT_CACHE_TIME, except_self=False,
                             cache_alias=DEFAULT_CACHE_ALIAS):
    """
    Just a decorator for cache result of a method
    """
    cache = caches[cache_alias]

    def cache_return_wrapper_inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _args = args[1:] if except_self else args
            cache_key = "{}_{}_{}".format(
                f.__name__,
                str(_args),
                str(frozenset(kwargs.items())),
            )
            cache_value = cache.get(cache_key)
            if not cache_value:
                cache_value = f(*args, **kwargs)
                cache.set(cache_key, cache_value, cache_time)
            return cache_value

        return wrapper
    if f:
        return cache_return_wrapper_inner(f)
    else:
        return cache_return_wrapper_inner


def to_timezone(dt, tz_name=settings.TIME_ZONE):
    """ Convert datetime to timezone datetime

    Args:
        dt (datetime) - The datetime object
        tz_name (str) - The name of timezone

    Returns:
        datetime - The datetime object with new timezone, invalid timezone
                   name make no effect

    """
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return dt

    return dt.astimezone(tz)


def format_date_time_zone(dt, f="%d/%m/%Y %H:%M:%S"):
    """
    Format datetime using TIME_ZONE in settings
    """
    try:
        return to_timezone(dt, settings.TIME_ZONE).strftime(f)
    except Exception:
        return dt
