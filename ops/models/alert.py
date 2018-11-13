#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/29 20:49
# @Author  : Dengsc
# @Site    : 
# @File    : alert.py
# @Software: PyCharm


from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Alert(models.Model):

    name = models.CharField(_('alert name'), unique=True, max_length=50)
    groups = models.ManyToManyField('AlertGroup',
                                    verbose_name=_('alert group'))
    level = models.ForeignKey('AlertLevel', verbose_name=_('alert level'),
                              related_name='level_alerts',
                              on_delete=models.CASCADE)
    ding_talk = models.ForeignKey('DingTalk',
                                  verbose_name=_('send ding talk'),
                                  related_name='ding_talk_alerts',
                                  on_delete=models.SET_NULL,
                                  null=True, blank=True)
    email = models.BooleanField(_('send email'), default=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              related_name='owner_alerts',
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class AlertGroup(models.Model):

    name = models.CharField(_('alert group name'), max_length=50, unique=True)
    users = models.ManyToManyField(User, verbose_name=_('alert user list'))
    last_modified_time = models.DateTimeField(_('last modified time'),
                                              auto_now=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              related_name='owner_alert_group',
                              null=True, blank=True)

    def __str__(self):
        return self.name


class AlertLevel(models.Model):

    name = models.CharField(_('level name'), max_length=50)
    desc = models.CharField(_('level description'), max_length=50)

    def __str__(self):
        return '{0}: {1}'.format(self.name, self.desc)


class AlertLog(models.Model):

    log_id = models.UUIDField(_('alert log uuid'), default=uuid4())
    alert = models.ForeignKey('Alert', verbose_name=_('alert'),
                              on_delete=models.SET_NULL, null=True)
    content = models.TextField(_('alert content'))
    status = models.BooleanField(_('send status'), default=True)

    def __str__(self):
        return '{0}'.format(self.log_id)


class DingTalk(models.Model):
    MSG_TYPES = (
        ('text', 'text'),
        ('markdown', 'markdown')
    )

    name = models.CharField(_('config name'), max_length=50, unique=True)
    url = models.URLField(_('ding talk request url'))
    msg_type = models.CharField(_('message type'), choices=MSG_TYPES,
                                default='markdown', max_length=20)
    at_all = models.BooleanField(_('@all'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
