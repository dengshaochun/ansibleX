#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/14 13:54
# @Author  : Dengsc
# @Site    : 
# @File    : handlers.py
# @Software: PyCharm

from django.dispatch import receiver
from django.db.models.signals import post_save

from ops.models import ProjectTask
from ops.tasks import run_project_task


@receiver(post_save, sender=ProjectTask, dispatch_uid='project_task_post_save')
def run_project_task_when_save(sender, **kwargs):
    task = kwargs.get('instance')
    if task.run:
        run_project_task(task_id=task.task_id).delay()
