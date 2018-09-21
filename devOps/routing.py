#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 15:30
# @Author  : Dengsc
# @Site    : 
# @File    : routing.py
# @Software: PyCharm


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
})
