#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 10:57
# @Author  : Dengsc
# @Site    : 
# @File    : redis_api.py
# @Software: PyCharm


import redis
import logging
from devOps.settings import REDIS_CONFIG

logger = logging.getLogger(__name__)


class RedisQueue(object):
    """Simple Queue with Redis Backend"""

    def __init__(self, name, namespace='queue'):
        """The default connection parameters are: 
        host='localhost', port=6379, db=0"""

        self.__db = redis.Redis(**REDIS_CONFIG)
        self.key = '%s:%s' % (namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.  

        If optional args block is true and timeout is None (the default), block 
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)

    def delete(self):
        """ Remove queue"""
        try:
            return self.__db.delete(self.key)
        except Exception as e:
            logger.exception(e)
            return False
