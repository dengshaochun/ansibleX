#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 19:13
# @Author  : Dengsc
# @Site    : 
# @File    : tasks.py
# @Software: PyCharm

import os
import time
from celery import shared_task
from django.conf import settings
from utils.ansible_api_v2.runner import AdHocRunner, PlaybookRunner
from ops.models import (Inventory, AnsiblePlayBook, AnsibleScript,
                        AnsibleRunning, AnsibleScriptLog, AnsiblePlayBookLog,
                        AnsibleModule)
from utils.redis_api import RedisQueue


def check_ready(obj_type, obj_id):
    redis_conn = RedisQueue(name=obj_id)
    if obj_type == 'script':
        obj = AnsibleScript.objects.get(script_id=obj_id)
    elif obj_type == 'playbook':
        obj = AnsiblePlayBook.objects.get(playbook_id=obj_id)
    elif obj_type == 'command':
        obj = AnsibleModule.objects.get(module_id=obj_id)
    else:
        raise Exception('Not support type: {0} !'.format(obj_type))

    if not obj.concurrent:
        while True:
            lock = AnsibleRunning.objects.filter(ansible_type=obj_type,
                                                 running_id=obj_id).first()
            if not lock:
                break
            redis_conn.put('Another same {0} is running, waiting...'.format(
                obj_type))
            time.sleep(10)

    AnsibleRunning(ansible_type=obj_type, running_id=obj_id)
    redis_conn.put(settings.ANSIBLE_TASK_START_PREFIX)
    return obj


def release_lock(obj_type, obj_id):
    redis_conn = RedisQueue(name=obj_id)
    lock = AnsibleRunning.objects.filter(ansible_type=obj_type,
                                         running_id=obj_id).first()
    if lock:
        lock.delete()
    redis_conn.put(settings.ANSIBLE_TASK_END_PREFIX)


@shared_task
def exec_ansible_script(log_id, script_id, inventory_id):

    succeed = True
    script_obj = check_ready('script', script_id)
    inventory_obj = Inventory.objects.get(inventory_id=inventory_id)
    log_path = os.path.join(settings.MEDIA_ROOT, 'logs', 'ansible', log_id)
    extra_vars = [script_obj.get_json_extra_vars(), ] if script_obj.extra_vars else []
    runner = AdHocRunner(
        module_name=script_obj.ansible_module.name,
        module_args=script_obj.args,
        hosts=inventory_obj.get_json_inventory(),
        log_path=log_path,
        log_id=log_id,
        extra_vars=extra_vars
    )
    try:
        result = runner.run()
    except Exception as e:
        result = {'Error': str(e)}
        succeed = False
    finally:
        release_lock('script', script_id)
    AnsibleScriptLog(log_id=log_id, script=script_obj,
                     inventory=inventory_obj, simple_log=log_path,
                     full_log=result, succeed=succeed).save()
    return result


@shared_task
def exec_ansible_playbook(log_id, playbook_id, inventory_id):

    succeed = True
    playbook_obj = check_ready('playbook', playbook_id)
    inventory_obj = Inventory.objects.get(inventory_id=inventory_id)
    log_path = os.path.join(settings.MEDIA_ROOT, 'logs', 'ansible', log_id)
    runner = PlaybookRunner(
        playbook_path=playbook_obj.file.path,
        hosts=inventory_obj.get_json_inventory(),
        log_path=os.path.join(settings.MEDIA_ROOT, 'logs', 'ansible', log_id),
        log_id=log_id,
        roles_path=None,
        extra_vars=[playbook_obj.get_json_extra_vars(), ]
    )
    try:
        result = runner.run()
    except Exception as e:
        result = {'Error': str(e)}
        succeed = False
    finally:
        release_lock('playbook', playbook_id)
    AnsiblePlayBookLog(log_id=log_id, playbook=playbook_obj,
                       inventory=inventory_obj, simple_log=log_path,
                       full_log=result, succeed=succeed).save()
    return result
