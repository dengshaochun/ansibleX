#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 15:50
# @Author  : Dengsc
# @Site    : 
# @File    : alert.py
# @Software: PyCharm

import json
import markdown
import requests
import logging
from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from django.conf import settings
from ops.models import Alert, AlertLog


logger = logging.getLogger(__name__)


class AlertSender(object):

    def __init__(self, alert_name, message):
        self.alert_obj = Alert.objects.get(name=alert_name)
        self.ding_talk = self.alert_obj.ding_talk
        self.email = self.alert_obj.email
        self.message = message
        self.alert_users = []
        self.subject = '[{0} Alert] - from devOps'.format(
            self.alert_obj.level.name)
        self.status = False
        self.html_message = markdown.markdown(message)

        self._get_alert_users()

    def _get_alert_users(self):
        for group in self.alert_obj.groups.all():
            for user in group.users.all():
                if user.profile.active:
                    self.alert_users.append(user.profile)

    def _send_email(self):
        email_users = [x.email for x in self.alert_users if x.email]
        msg = EmailMultiAlternatives(self.subject,
                                     'receive new alert',
                                     settings.EMAIL_FROM,
                                     email_users)
        msg.attach_alternative(self.html_message, 'text/html')
        msg.send()

    def _send_ding_talk(self):
        result = requests.post(
            url=self.ding_talk.url,
            headers={'Content-Type': 'application/json'},
            data=self._get_ding_talk_data()
        )
        result.raise_for_status()

    def _get_ding_talk_data(self):

        at_dict = {
            'atMobiles': None,
            'isAtAll': 'false'
        }

        text_dict = {
            'msgtype': 'text',
            'text': {
                'content': None
            },
            'at': None
        }

        markdown_dict = {
            'msgtype': 'markdown',
            'markdown': {
                'title': None,
                'text': None
            },
            'at': None
        }

        mobiles = [x.phone for x in self.alert_users if x.phone]
        at_content = '\n \n \n' + ' '.join(['@{0}'.format(x) for x in mobiles])
        at_dict['atMobiles'] = mobiles
        if self.ding_talk.at_all:
            at_dict['isAtAll'] = 'true'

        if self.ding_talk.msg_type == 'markdown':
            markdown_dict['markdown']['title'] = self.subject
            markdown_dict['markdown']['text'] = self.message + at_content
            content = markdown_dict
        else:
            text_dict['text']['content'] = self.html_message + at_content
            content = text_dict
        content['at'] = at_dict

        return json.dumps(content)

    def run(self):
        try:
            if self.email:
                self._send_email()
            if self.ding_talk:
                self._send_ding_talk()
            self.status = True
        except Exception as e:
            logger.exception(e)
            self.status = False
        finally:
            AlertLog(alert=self.alert_obj,
                     content=self.message, status=self.status).save()
        return self.status


@shared_task
def run_alert_task(alert_name, message):
    return AlertSender(alert_name, message).run()
