#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/14 13:54
# @Author  : Dengsc
# @Site    : 
# @File    : handlers.py
# @Software: PyCharm

import json
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django_celery_beat.models import PeriodicTask
from ops.models import (AnsibleScriptTaskSchedule, AnsiblePlayBookTaskSchedule,
                        ProjectTask, AnsibleScriptTask, AnsiblePlayBookTask)
from ops.tasks import (run_project_task, run_ansible_script_task,
                       run_ansible_playbook_task)


@receiver(post_save, sender=ProjectTask, dispatch_uid='project_task_post_save')
def run_project_task_when_save(sender, **kwargs):
    task = kwargs.get('instance')
    if task.run_on_save:
        run_project_task.delay(task_id='{0}'.format(task.task_id))


@receiver(post_save, sender=AnsibleScriptTask,
          dispatch_uid='ansible_script_task_post_save')
def run_ansible_script_task_when_save(sender, **kwargs):
    task = kwargs.get('instance')
    if task.run_on_save:
        run_ansible_script_task.delay(task_id='{0}'.format(task.task_id))


@receiver(post_save, sender=AnsiblePlayBookTask,
          dispatch_uid='ansible_playbook_task_post_save')
def run_ansible_playbook_task_when_save(sender, **kwargs):
    task = kwargs.get('instance')
    if task.run_on_save:
        run_ansible_playbook_task.delay(task_id='{0}'.format(task.task_id))


@receiver(post_save, sender=AnsibleScriptTaskSchedule,
          dispatch_uid='ansible_script_task_schedule_post_save')
def setup_ansible_task_schedule(sender, **kwargs):
    schedule = kwargs.get('instance')
    task_name = '{0}-{1}-{2}'.format('script',
                                     schedule.task.owner.username,
                                     schedule.name)

    pt = PeriodicTask.objects.filter(name=task_name).first()
    if not pt:
        pt = PeriodicTask()
        pt.name = task_name
        pt.task = 'ops.tasks.run_ansible_script_task'
    pt.crontab = schedule.crontab
    pt.interval = schedule.interval
    pt.kwargs = json.dumps({'task_id': '{0}'.format(schedule.task.task_id)})
    pt.enabled = schedule.enabled
    pt.save()


@receiver(post_delete, sender=AnsibleScriptTaskSchedule,
          dispatch_uid='ansible_script_task_schedule_post_delete')
def uninstall_ansible_task_schedule(sender, **kwargs):
    schedule = kwargs.get('instance')
    task_name = '{0}-{1}-{2}'.format('script',
                                     schedule.task.owner.username,
                                     schedule.name)

    pt = PeriodicTask.objects.filter(name=task_name).first()
    if pt:
        pt.delete()


@receiver(post_save, sender=AnsiblePlayBookTaskSchedule,
          dispatch_uid='ansible_playbook_task_schedule_post_save')
def setup_ansible_playbook_schedule(sender, **kwargs):
    schedule = kwargs.get('instance')
    task_name = '{0}-{1}-{2}'.format('playbook',
                                     schedule.task.owner.username,
                                     schedule.name)

    pt = PeriodicTask.objects.filter(name=task_name).first()
    if not pt:
        pt = PeriodicTask()
        pt.name = task_name
        pt.task = 'ops.tasks.run_ansible_playbook_task'
    pt.crontab = schedule.crontab
    pt.interval = schedule.interval
    pt.enabled = schedule.enabled
    pt.kwargs = json.dumps({'task_id': '{0}'.format(schedule.task.task_id)})
    pt.save()


@receiver(post_delete, sender=AnsiblePlayBookTaskSchedule,
          dispatch_uid='ansible_playbook_task_schedule_post_delete')
def uninstall_ansible_playbook_schedule(sender, **kwargs):
    schedule = kwargs.get('instance')
    task_name = '{0}-{1}-{2}'.format('playbook',
                                     schedule.task.owner.username,
                                     schedule.name)

    pt = PeriodicTask.objects.filter(name=task_name).first()
    if pt:
        pt.delete()
