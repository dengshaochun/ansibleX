#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/8 13:47
# @Author  : Dengsc
# @Site    : 
# @File    : display.py
# @Software: PyCharm


from __future__ import absolute_import

import os
import sys
import datetime
import getpass

from ansible.utils.display import Display
from ansible.utils.color import stringc
from ansible import constants as C
from ansible.module_utils._text import to_bytes, to_text

from utils.redis_api import RedisQueue


class MyDisplay(Display):
    
    def __init__(self, verbosity=0, log_id=None, log_path=None):

        self.log_path = log_path
        self.log_id = log_id
        self.redis = None
        self._set_redis()

        super(MyDisplay, self).__init__(verbosity)

    def _write_log(self, msg, level='INFO'):
        if self.log_path and (
            os.path.exists(self.log_path)
                and os.access(self.log_path, os.W_OK)) \
                or os.access(os.path.dirname(self.log_path), os.W_OK):
            mypid = str(os.getpid())
            user = getpass.getuser()
            prefix = "p=%s u=%s" % (mypid, user)
            msg = ' | '.join([str(datetime.datetime.now()), prefix, level, msg])
            with open(self.log_path, 'a+') as fs:
                fs.write(msg)
                fs.write('\n')

    def _set_redis(self):
        if self.log_id:
            self.redis = RedisQueue(name=self.log_id)

    def display(self, msg, color=None, stderr=False,
                screen_only=False, log_only=False):
        """ Display a message to the user

        Note: msg *must* be a unicode string to prevent UnicodeError tracebacks.
        """

        nocolor = msg
        if color:
            msg = stringc(msg, color)

        if not log_only:
            if not msg.endswith(u'\n'):
                msg2 = msg + u'\n'
            else:
                msg2 = msg

            msg2 = to_bytes(msg2, encoding=self._output_encoding(stderr=stderr))
            if sys.version_info >= (3,):
                msg2 = to_text(msg2, self._output_encoding(stderr=stderr),
                               errors='replace')

            if self.redis:
                self.redis.put(msg2)

        if self.log_path and not screen_only:
            msg2 = nocolor.lstrip(u'\n')

            msg2 = to_bytes(msg2)
            if sys.version_info >= (3,):
                # Convert back to text string on python3
                # We first convert to a byte string so that we get rid of
                # characters that are invalid in the user's locale
                msg2 = to_text(msg2, self._output_encoding(stderr=stderr))

            if color == C.COLOR_ERROR:
                self._write_log(msg=msg2, level='ERROR')
            else:
                self._write_log(msg=msg2, level='INFO')
