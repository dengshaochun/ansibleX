#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 19:13
# @Author  : Dengsc
# @Site    : 
# @File    : tasks.py
# @Software: PyCharm

import os
import time
import yaml
import logging
from celery import shared_task
from django.conf import settings
from utils.ansible_api_v2.runner import AdHocRunner, PlaybookRunner
from ops.models import (Inventory, AnsiblePlayBook, AnsibleScript,
                        AnsibleRunning, AnsibleExecLog, AnsibleConfig)
from utils.ansible_api_v2.display import MyDisplay

logger = logging.getLogger(__name__)


def check_ready(obj_type, obj_id, display):
    if obj_type == 'script':
        obj = AnsibleScript.objects.get(script_id=obj_id)
    elif obj_type == 'playbook':
        obj = AnsiblePlayBook.objects.get(playbook_id=obj_id)
    else:
        raise Exception('Not support type: {0} !'.format(obj_type))

    if not obj.concurrent:
        while True:
            lock = AnsibleRunning.objects.filter(ansible_type=obj_type,
                                                 running_id=obj_id).first()
            if not lock:
                break
            display.display('Another same {0} is running, waiting...'.format(
                obj_type))
            time.sleep(10)

    AnsibleRunning(ansible_type=obj_type, running_id=obj_id)
    display.display(settings.ANSIBLE_TASK_START_PREFIX)
    return obj


def release_lock(obj_type, obj_id, display):
    try:
        lock = AnsibleRunning.objects.filter(ansible_type=obj_type,
                                             running_id=obj_id).first()
        if lock:
            lock.delete()
        display.display(settings.ANSIBLE_TASK_END_PREFIX)
    except Exception as e:
        logger.exception(e)


def save_execute_log(log_id, ansible_type, object_id, inventory_id, config_id,
                     succeed, full_log, user_input):

    try:
        AnsibleExecLog(
            log_id=log_id,
            ansible_type=ansible_type,
            object_id=object_id,
            inventory_id=inventory_id,
            config_id=config_id,
            succeed=succeed,
            full_log=full_log,
            user_input=user_input,
        ).save()
    except Exception as e:
        logger.exception(e)


@shared_task
def exec_ansible_script(log_id, script_id, inventory_id,
                        config_id, **user_input):

    succeed = True
    ansible_type = 'script'
    log_path = os.path.join(settings.ANSIBLE_BASE_LOG_DIR, log_id)
    display = MyDisplay(log_id=log_id, log_path=log_path)

    try:
        script_obj = check_ready(ansible_type, script_id, display)
        inventory_obj = Inventory.objects.get(inventory_id=inventory_id)

        if user_input.get('module_args'):
            module_args = user_input.get('module_args')
        else:
            module_args = script_obj.module_args
        extra_vars = script_obj.get_json_extra_vars()
        if user_input.get('extra_vars'):
            extra_vars.update(
                dict(yaml.safe_load(user_input.get('extra_vars'))))

        kwargs = AnsibleConfig.objects.get(
            config_id=config_id).get_json_config()
        kwargs['extra_vars'] = [extra_vars]

        runner = AdHocRunner(
            module_name=script_obj.ansible_module.name,
            module_args=module_args,
            hosts=inventory_obj.get_json_inventory(),
            log_path=log_path,
            log_id=log_id,
            **kwargs
        )
        succeed, result = runner.run()
    except Exception as e:
        result = str(e)
        succeed = False
        display.display(result, stderr=True)
    finally:
        release_lock(ansible_type, script_id, display)
    save_execute_log(log_id, ansible_type, script_id,
                     inventory_id, config_id, succeed, result, user_input)
    return result


@shared_task
def exec_ansible_playbook(log_id, playbook_id, inventory_id,
                          config_id, **user_input):

    ansible_type = 'playbook'
    log_path = os.path.join(settings.ANSIBLE_BASE_LOG_DIR, log_id)
    display = MyDisplay(log_id=log_id, log_path=log_path)

    try:
        playbook_obj = check_ready(ansible_type, playbook_id, display)
        inventory_obj = Inventory.objects.get(inventory_id=inventory_id)

        extra_vars = playbook_obj.get_json_extra_vars()
        if user_input.get('extra_vars'):
            extra_vars.update(
                dict(yaml.safe_load(user_input.get('extra_vars'))))

        kwargs = AnsibleConfig.objects.get(
            config_id=config_id).get_json_config()
        kwargs['extra_vars'] = [extra_vars, ]

        runner = PlaybookRunner(
            playbook_path=playbook_obj.file_path.path,
            hosts=inventory_obj.get_json_inventory(),
            log_path=log_path,
            log_id=log_id,
            roles_path=None,
            **kwargs
        )
        succeed, result = runner.run()
    except Exception as e:
        result = str(e)
        succeed = False
        display.display(result, stderr=True)
    finally:
        release_lock(ansible_type, playbook_id, display)
    save_execute_log(log_id, ansible_type, playbook_id,
                     inventory_id, config_id, succeed, result, user_input)
    return result
