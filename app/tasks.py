#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/26 20:16
# @Author  : Dengsc
# @Site    : 
# @File    : tasks.py
# @Software: PyCharm


# Create your tasks here
from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task
from utils.ansible_api_v2.runner import AdHocRunner, PlaybookRunner
from ops.models import Inventory
from devOps.settings import BASE_DIR
import os


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def test_ad_hoc(command, command_args,
                log_id='ad_hoc_{}'.format(str(time.time() * 1000))):

    runner = AdHocRunner(
        module_name=command,
        module_args=command_args,
        remote_user='dengsc',
        hosts=Inventory.objects.first().get_json_inventory(),
        log_path=os.path.join(BASE_DIR, 'logs', 'ansible', log_id),
        log_id=log_id,
    )
    return runner.run()


@shared_task
def test_playbook(log_id='playbook_{}'.format(str(time.time() * 1000))):
    runner = PlaybookRunner(
        playbook_path=os.path.join(BASE_DIR, 'files', 'debug.yml'),
        hosts='localhost',
        remote_user='dengsc',
        log_path=os.path.join(BASE_DIR, 'logs', 'ansible', log_id),
        log_id=log_id,
        roles_path=None,
        extra_vars=[{'host_list': 'all'}, ]
    )

    return runner.run()
