""" Caching module
"""
try:
    from eea.cache import cache as eeacache
    from eea.cache import event
    # pyflakes
    InvalidateCacheEvent = event.InvalidateCacheEvent
    ramcache = eeacache
except ImportError:
    # Fail quiet if required cache packages are not installed in order to use
    # this package without caching
    from eea.app.visualization.cache.nocache import ramcache
    from eea.app.visualization.cache.nocache import InvalidateCacheEvent

from eea.app.visualization.cache.cache import cacheJsonKey

__all__ = [
    ramcache.__name__,
    InvalidateCacheEvent.__name__,
    cacheJsonKey.__name__,
]
