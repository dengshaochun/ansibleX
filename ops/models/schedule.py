#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/9 17:34
# @Author  : Dengsc
# @Site    : 
# @File    : schedule.py
# @Software: PyCharm


from django.db import models
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask
from django.utils.translation import ugettext_lazy as _


class UserSchedule(models.Model):

    task = models.ForeignKey(PeriodicTask, verbose_name=_('schedule task'),
                             on_delete=models.CASCADE,
                             related_name='task_user_schedules')
    owner = models.ForeignKey(User, verbose_name=_('schedule task owner'),
                              related_name='owner_user_schedules',
                              on_delete=models.CASCADE)
    created_time = models.DateTimeField(_('created time'), auto_now=True)

    def __str__(self):
        return '{0}: {1}'.format(self.task, self.owner)
