#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 15:56
# @Author  : Dengsc
# @Site    : 
# @File    : consumers.py
# @Software: PyCharm


from channels.generic.websocket import WebsocketConsumer
from utils.redis_api import RedisQueue
from django.conf import settings
import json


class LogsConsumer(WebsocketConsumer):
    def connect(self):
        self.log_id = self.scope['url_route']['kwargs']['log_id']

        self.accept()

        redis = RedisQueue(name=self.log_id)
        message = redis.get(timeout=10).decode('utf-8')
        while message != settings.ANSIBLE_TASK_END_PREFIX:
            if message:
                # Send message to room group
                print('send: ' + str(message))
                self.send(text_data=json.dumps({
                    'message': str(message)
                }))
            message = redis.get(timeout=10).decode('utf-8')
