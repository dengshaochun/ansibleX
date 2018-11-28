#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/15 10:51
# @Author  : Dengsc
# @Site    : 
# @File    : schedule.py
# @Software: PyCharm


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import (CrontabSchedule, IntervalSchedule)
from django.core.exceptions import ValidationError

from ops.models.ansible import AnsiblePlayBookTask, AnsibleScriptTask
from ops.models.project import ProjectTask


class ScheduleTaskBase(models.Model):

    name = models.CharField(_('schedule task name'), max_length=100,
                            unique=True)
    crontab = models.ForeignKey(
        CrontabSchedule, verbose_name=_('crontab'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='crontab_schedule_base_schedules')
    interval = models.ForeignKey(
        IntervalSchedule, verbose_name=_('interval'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interval_schedule_base_schedules')
    enabled = models.BooleanField(_('enable'), default=True)

    def validate_unique(self, *args, **kwargs):
        super(ScheduleTaskBase, self).validate_unique(*args, **kwargs)
        if not self.interval and not self.crontab:
            raise ValidationError({
                'interval': [
                    'One of interval, crontab must be set.'
                ]
            })
        if self.interval and self.crontab:
            raise ValidationError({
                'crontab': [
                    'Only one of interval, crontab must be set'
                ]
            })

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class AnsibleScriptTaskSchedule(ScheduleTaskBase):

    task = models.ForeignKey(AnsibleScriptTask, verbose_name=_('task'),
                             related_name='ansible_script_schedules',
                             on_delete=models.CASCADE)
    crontab = models.ForeignKey(
        CrontabSchedule, verbose_name=_('crontab'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='crontab_ansible_script_schedules')
    interval = models.ForeignKey(
        IntervalSchedule, verbose_name=_('interval'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interval_ansible_script_schedules')


class AnsiblePlayBookTaskSchedule(ScheduleTaskBase):

    task = models.ForeignKey(AnsiblePlayBookTask, verbose_name=_('task'),
                             related_name='ansible_playbook_schedules',
                             on_delete=models.CASCADE)
    crontab = models.ForeignKey(
        CrontabSchedule, verbose_name=_('crontab'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='crontab_ansible_playbook_schedules')
    interval = models.ForeignKey(
        IntervalSchedule, verbose_name=_('interval'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interval_ansible_playbook_schedules')


class ProjectTaskSchedule(ScheduleTaskBase):

    task = models.ForeignKey(ProjectTask, verbose_name=_('task'),
                             related_name='task_project_schedules',
                             on_delete=models.CASCADE)
    crontab = models.ForeignKey(
        CrontabSchedule, verbose_name=_('crontab'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='crontab_project_schedules')
    interval = models.ForeignKey(
        IntervalSchedule, verbose_name=_('interval'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interval_project_schedules')
