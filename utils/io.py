"""This module provides facilities with regard to caching results to
disk. These functions are meant to speed up functions when no better
ways are available. Functions included:
    cache
    matcache

1-14-2017
"""

import os
from scipy import io
import functools
import msgpack


def cache(function):
    """Generic caching wrapper. Should work on any kind of I/O"""
    @functools.wraps(function)
    def wrapper(*args, **kargs):
        cachefile = '/tmp/spinsys/{}{}.mp'.format(function.__name__,
                                                  (args, kargs))
        if not os.path.isdir('/tmp/spinsys/'):
            os.mkdir('/tmp/spinsys/')
        try:
            with open(cachefile, 'rb') as c:
                return msgpack.load(c)
        except FileNotFoundError:
            result = function(*args, **kargs)
            with open(cachefile, 'wb') as c:
                msgpack.dump(result, c)
            return result
    return wrapper


def matcache(function):
    """Caching wrapper for sparse matrix generating functions."""
    @functools.wraps(function)
    def wrapper(*args, **kargs):
        cachefile = '/tmp/spinsys/{}{}.mat'.format(function.__name__,
                                                   (args, kargs))
        if not os.path.isdir('/tmp/spinsys/'):
            os.mkdir('/tmp/spinsys/')
        try:
            return io.loadmat(cachefile)['i']
        except FileNotFoundError:
            result = function(*args, **kargs)
            io.savemat(cachefile, {'i': result}, appendmat=False)
            return result
    return wrapper