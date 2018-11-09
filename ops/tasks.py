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
import shutil
import logging
import datetime
from utils.git_api import GitUtil
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from utils.ansible_api_v2.runner import AdHocRunner, PlaybookRunner
from ops.models import (Inventory, AnsiblePlayBook, AnsibleScript,
                        AnsibleLock, AnsibleExecLog, AnsibleConfig,
                        GitProject, ProjectActionLog)
from utils.ansible_api_v2.display import MyDisplay

logger = logging.getLogger(__name__)


def ansible_run_before(**kwargs):
    ansible_type = kwargs.get('ansible_type')
    object_id = kwargs.get('object_id')
    display = kwargs.get('display')
    if ansible_type == 'script':
        obj = AnsibleScript.objects.get(script_id=object_id)
    elif ansible_type == 'playbook':
        obj = AnsiblePlayBook.objects.get(playbook_id=object_id)
    else:
        raise Exception('Not support type: {0} !'.format(ansible_type))

    if not obj.concurrent:
        while True:
            lock = AnsibleLock.objects.filter(ansible_type=ansible_type,
                                              lock_object_id=object_id).first()
            if not lock:
                break
            display.display('Another same {0} is running, waiting...'.format(
                ansible_type))
            time.sleep(10)

    AnsibleLock(ansible_type=ansible_type, lock_object_id=object_id)
    display.display(settings.ANSIBLE_TASK_START_PREFIX)
    return obj


def release_lock(**kwargs):
    ansible_type = kwargs.get('ansible_type')
    object_id = kwargs.get('object_id')
    display = kwargs.get('display')
    try:
        lock = AnsibleLock.objects.filter(ansible_type=ansible_type,
                                          lock_object_id=object_id).first()
        if lock:
            lock.delete()
        display.display(settings.ANSIBLE_TASK_END_PREFIX)
    except Exception as e:
        logger.exception(e)


def ansible_run_end(**kwargs):

    message_template = r'''
    [task type]: {ansible_type}
    [task status]: {succeed}
    [task execute user]: {exec_user}
    [task log url]: {full_log}
    '''

    try:
        log_obj = AnsibleExecLog(
            log_id=kwargs.get('log_id'),
            ansible_type=kwargs.get('ansible_type'),
            object_id=kwargs.get('object_id'),
            inventory_id=kwargs.get('inventory_id'),
            config_id=kwargs.get('config_id'),
            succeed=kwargs.get('succeed'),
            user_raw=kwargs.get('user_input'),
            completed_log=kwargs.get('result'),
            exec_user=kwargs.get('exec_user')
        )
        log_obj.save()
        current_obj = kwargs.get('current_obj')
        if current_obj.alert:
            if current_obj.alert_succeed or current_obj.alert_failed:
                send_alert(current_obj.alert.alert_id, message_template.format(
                    ansible_type=kwargs.get('ansible_type'),
                    succeed=kwargs.get('succeed'),
                    exec_user=kwargs.get('exec_user'),
                    full_log=log_obj.full_log.url
                ))
    except Exception as e:
        logger.exception(e)


@shared_task
def run_ansible(ansible_type, log_id, object_id, inventory_id,
                config_id, user_id, **user_input):

    runner = None
    # current year and month
    yy_mm = datetime.datetime.now().strftime('%Y%m')
    # define log path
    log_path = os.path.join(settings.ANSIBLE_BASE_LOG_DIR, yy_mm, log_id)
    # define ansible display
    display = MyDisplay(log_id=log_id, log_path=log_path)
    # define execute user
    exec_user = User.objects.get(pk=user_id)
    current_obj = ansible_run_before(**locals())
    inventory_obj = Inventory.objects.get(inventory_id=inventory_id)
    extra_vars = current_obj.get_json_extra_vars()
    if user_input.get('extra_vars'):
        extra_vars.update(
            dict(yaml.safe_load(user_input.get('extra_vars'))))

    kwargs = AnsibleConfig.objects.get(
        config_id=config_id).get_json_config()
    kwargs['extra_vars'] = [extra_vars, ]

    if ansible_type == 'script':
        if user_input.get('module_args'):
            module_args = user_input.get('module_args')
        else:
            module_args = current_obj.module_args

        runner = AdHocRunner(
            module_name=current_obj.ansible_module.name,
            module_args=module_args,
            hosts=inventory_obj.get_json_inventory(),
            log_path=log_path,
            log_id=log_id,
            **kwargs
        )
    elif ansible_type == 'playbook':
        runner = PlaybookRunner(
            playbook_path=current_obj.file_path.path,
            hosts=inventory_obj.get_json_inventory(),
            log_path=log_path,
            log_id=log_id,
            roles_path=None,
            **kwargs
        )
    try:
        if runner:
            succeed, result = runner.run()
        else:
            succeed = False
            result = {'error': 'runner is not defined!'}
    except Exception as e:
        result = str(e)
        succeed = False
        display.display(result, stderr=True)
    finally:
        release_lock(**locals())
    # save log
    ansible_run_end(**locals())
    return result


@shared_task
def run_project_command(project_id, action_type, user_id):

    _status = {
        'succeed': False,
        'msg': ''
    }

    def clean_local_path():
        if project.local_dir:
            if os.path.exists(project.local_dir):
                shutil.rmtree(project.local_dir)
                _status['succeed'] = True
                _status['msg'] = 'Remove local path : {0} successful!'.format(
                    project.local_dir)
            else:
                _status['msg'] = 'Local path: {0} do not exists!'.format(
                    project.local_dir)
        else:
            _status['msg'] = 'local_dir field is null!'

    def clone_project():
        result = repo.clone()
        project.local_dir = repo.local_path
        if result.get('succeed'):
            project.current_version = result.get('etc', {}).get('version')
            project.save()

        _status['succeed'] = result.get('succeed')
        _status['msg'] = result.get('msg')

    def pull_project():
        result = repo.pull()
        if result.get('succeed'):
            project.current_version = result.get('etc', {}).get('version')
            project.save()

        _status['succeed'] = result.get('succeed')
        _status['msg'] = result.get('msg')

    def find_playbooks():
        _add = 0
        _skip = 0
        try:
            playbook_path = os.path.join(project.local_dir, 'playbooks')
            role_path = os.path.join(project.local_dir, 'roles')
            playbooks = os.listdir(playbook_path)
            for playbook in playbooks:
                if playbook.endswith('.yml'):
                    obj = AnsiblePlayBook.objects.filter(
                        name=playbook,
                        project=project
                    ).first()
                    if not obj:
                        AnsiblePlayBook(name=playbook,
                                        file_path=os.path.join(playbook_path,
                                                               playbook),
                                        role_path=role_path,
                                        project=project).save()
                        _add += 1
                    else:
                        _skip += 1
            _status['succeed'] = True
            _status['msg'] = 'New add {0}, Skip {1}!'.format(_add, _skip)
        except Exception as e:
            _status['msg'] = str(e)

    project = GitProject.objects.filter(project_id=project_id).first()

    if project and project.active:

        repo = GitUtil(project.remote_url, project_id,
                       project.auth_user, project.token)

        if action_type == 'clone':
            clone_project()
        elif action_type == 'pull':
            pull_project()
        elif action_type == 'clean':
            clean_local_path()
        elif action_type == 'find':
            find_playbooks()
        else:
            _status['msg'] = 'Not supported Action [{0}]!'.format(action_type)
    else:
        _status['msg'] = 'Project is inactive or not exists! action canceled!'

    ProjectActionLog(action_status=_status.get('succeed'),
                     project=project,
                     action_type=action_type,
                     action_log=_status.get('msg'),
                     exec_user=User.objects.get(pk=user_id)).save()
    return _status


@shared_task
def send_alert(alert_id, message):
    pass
