#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/26 20:10
# @Author  : Dengsc
# @Site    :
# @File    : __init_.py
# @Software: PyCharm


from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app', )
