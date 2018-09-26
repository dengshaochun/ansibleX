#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/26 20:16
# @Author  : Dengsc
# @Site    : 
# @File    : tasks.py
# @Software: PyCharm


# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
