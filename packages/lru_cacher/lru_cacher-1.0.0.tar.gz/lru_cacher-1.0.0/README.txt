lru_cacher
=========

This is a  Least Recently Used (LRU) Cache implementation in Python.

INSTALLATION

To install, simply run
python setup.py install

To run unit tests, run
python setup.py test


EXAMPLE USAGE

>>> from time import sleep
>>>
>>> from lru_cacher import LruCacher
>>>
>>> def slowSqrt(n):
>>>   sleep(2)
>>>   return n**0.5

>>> cache = LruCache(max_size=200)
#This lookup will be slow
>>> answer, found_in_cache = cache.lookup(49)
>>> print answer, found_in_cache
7.0 False

#This lookup will be fast
>>> answer, found_in_cache = cache.lookup(49)
>>> print answer, found_in_cache
7.0 True

#Let's modify the cache
>>> cache.update(49, 'seven')
>>> answer, found_in_cache = cache.lookup(49)
>>> print answer, found_in_cache
seven True