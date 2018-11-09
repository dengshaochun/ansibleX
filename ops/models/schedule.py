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

    task = models.OneToOneField(PeriodicTask, verbose_name=_('schedule task'),
                                on_delete=models.CASCADE)
    owner = models.ForeignKey(User, verbose_name=_('schedule task owner'),
                              on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1}'.format(self.task.name, self.owner.username)
