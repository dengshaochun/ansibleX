#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 15:57
# @Author  : Dengsc
# @Site    : 
# @File    : routing.py
# @Software: PyCharm


from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
]
