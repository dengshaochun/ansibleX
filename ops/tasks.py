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


class Ansible(object):

    def __init__(self, ansible_type, log_id, object_id, inventory_id,
                 config_id, user_id, **user_input):

        self.ansible_type = ansible_type
        self.log_id = log_id
        self.object_id = object_id
        self.user_id = user_id
        self.config_id = config_id
        self.user_input = user_input
        self.inventory_id = inventory_id

        self.succeed = False
        self.result = None
        self.log_obj = None

        # current year and month
        yy_mm = datetime.datetime.now().strftime('%Y%m')
        # define log path
        self.log_path = os.path.join(settings.ANSIBLE_BASE_LOG_DIR,
                                     yy_mm, self.log_id)
        # define ansible display
        self.display = MyDisplay(log_id=self.log_id, log_path=self.log_path)
        # define execute user
        self.exec_user = User.objects.get(pk=self.user_id)

        # get ansible object
        if self.ansible_type == 'script':
            self.current_obj = AnsibleScript.objects.get(
                script_id=self.object_id)
            if self.user_input.get('module_args'):
                self.module_args = self.user_input.get('module_args')
            else:
                self.module_args = self.current_obj.module_args
        elif self.ansible_type == 'playbook':
            self.current_obj = AnsiblePlayBook.objects.get(
                playbook_id=self.object_id)
        else:
            raise Exception('Not support ansible type: {0} !'.format(
                self.ansible_type))

        self.inventory_obj = Inventory.objects.get(inventory_id=inventory_id)
        self.extra_vars = self.current_obj.get_json_extra_vars()
        if self.user_input.get('extra_vars'):
            self.extra_vars.update(
                dict(yaml.safe_load(user_input.get('extra_vars'))))

        self.kwargs = AnsibleConfig.objects.get(
            config_id=self.config_id).get_json_config()
        self.kwargs['extra_vars'] = [self.extra_vars, ]

        self.runner = self._get_runner()

    def _get_runner(self):
        if self.ansible_type == 'script':
            runner = AdHocRunner(
                module_name=self.current_obj.ansible_module.name,
                module_args=self.module_args,
                hosts=self.inventory_obj.get_json_inventory(),
                log_path=self.log_path,
                log_id=self.log_id,
                **self.kwargs
            )
        else:
            runner = PlaybookRunner(
                playbook_path=self.current_obj.file_path.path,
                hosts=self.inventory_obj.get_json_inventory(),
                log_path=self.log_path,
                log_id=self.log_id,
                roles_path=self.current_obj.role_path or None,
                **self.kwargs
            )
        return runner

    def run(self):
        try:
            if self.runner:
                self._run_before()
                self.succeed, self.result = self.runner.run()
            else:
                self.result = {'error': 'runner is not defined!'}
        except Exception as e:
            self.result = str(e)
            self.display.display(self.result, stderr=True)
        finally:
            self._run_end()
        return self.result

    def _run_before(self):
        if not self.current_obj.concurrent:
            while True:
                lock = AnsibleLock.objects.filter(
                    ansible_type=self.ansible_type,
                    lock_object_id=self.object_id).first()
                if not lock:
                    break
                self.display.display(
                    'Another same {0} is running, waiting...'.format(
                        self.ansible_type))
                time.sleep(10)

        AnsibleLock(ansible_type=self.ansible_type,
                    lock_object_id=self.object_id).save()
        self.display.display(settings.ANSIBLE_TASK_START_PREFIX)

    def _release_lock(self):
        try:
            # release lock
            lock = AnsibleLock.objects.filter(
                ansible_type=self.ansible_type,
                lock_object_id=self.object_id).first()
            if lock:
                lock.delete()
            self.display.display(settings.ANSIBLE_TASK_END_PREFIX)
        except Exception as e:
            logger.exception(e)

    def _save_log(self):
        try:
            # save log
            self.log_obj = AnsibleExecLog(
                log_id=self.log_id,
                ansible_type=self.ansible_type,
                object_id=self.object_id,
                inventory_id=self.inventory_id,
                config_id=self.config_id,
                succeed=self.succeed,
                user_raw=self.user_input,
                completed_log=self.result,
                exec_user=self.exec_user
            )
            self.log_obj.save()
        except Exception as e:
            logger.exception(e)

    def _send_alert(self):

        message_template = r'''
        [task type]: {ansible_type}
        [task status]: {succeed}
        [task execute user]: {exec_user}
        [task log url]: {full_log}
        '''

        # send alert
        if self.current_obj.alert and self.log_obj:
            if self.current_obj.alert_succeed or \
                    self.current_obj.alert_failed:
                run_alert_task(
                    self.current_obj.alert.name,
                    message_template.format(
                        ansible_type=self.ansible_type,
                        succeed=self.succeed,
                        exec_user=self.exec_user,
                        full_log=self.log_obj.full_log.url
                    ))

    def _run_end(self):
        self._release_lock()
        self._save_log()
        self._send_alert()


class Project(object):

    def __init__(self, project_id, action_type, user_id):
        self._status = {
            'succeed': False,
            'msg': ''
        }
        self.user_id = user_id
        self.action_type = action_type
        self.repo = None
        self.project = GitProject.objects.filter(project_id=project_id).first()
        if self.project and self.project.active:
            self.repo = GitUtil(self.project.remote_url, project_id,
                                self.project.auth_user, self.project.token)

    def _clean(self):
        local_path = self.project.local_dir or self.repo.local_path
        if local_path:
            if os.path.isdir(local_path):
                shutil.rmtree(local_path)
                self._status['succeed'] = True
                self._status['msg'] = 'Remove local path : {0} succeed!'.format(
                    local_path)
            else:
                self._status['msg'] = 'Local path: {0} do not exists!'.format(
                    local_path)
        else:
            self._status['msg'] = 'local dir not exists!'

    def _clone(self):
        result = self.repo.clone()
        self.project.local_dir = self.repo.local_path
        if result.get('succeed'):
            self.project.current_version = result.get(
                'etc', {}).get('version')
            self.project.save()

        self._status['succeed'] = result.get('succeed')
        self._status['msg'] = result.get('msg')

    def _pull(self):
        result = self.repo.pull()
        if result.get('succeed'):
            self.project.current_version = result.get(
                'etc', {}).get('version')
            self.project.save()

        self._status['succeed'] = result.get('succeed')
        self._status['msg'] = result.get('msg')

    def _find(self):
        _add = 0
        _skip = 0
        try:
            playbook_path = os.path.join(self.project.local_dir, 'playbooks')
            role_path = os.path.join(self.project.local_dir, 'roles')
            tmp = [os.path.join('playbooks', x) for x in
                   os.listdir(playbook_path)]
            tmp += [x for x in os.listdir(self.project.local_dir)]
            playbooks = [x for x in tmp if
                         x.endswith('.yml') or x.endswith('.yaml')]
            for playbook in playbooks:
                obj = AnsiblePlayBook.objects.filter(
                    name=playbook,
                    project=self.project
                ).first()
                if not obj:
                    AnsiblePlayBook(name=playbook,
                                    file_path=os.path.join(
                                        self.project.local_dir, playbook),
                                    role_path=role_path,
                                    project=self.project).save()
                    _add += 1
                else:
                    _skip += 1
            self._status['succeed'] = True
            self._status['msg'] = 'playbook add {0}, skip {1}!'.format(
                _add, _skip)
        except Exception as e:
            self._status['msg'] = str(e)

    def _save_log(self):
        try:
            ProjectActionLog(action_status=self._status.get('succeed'),
                             project=self.project,
                             action_type=self.action_type,
                             action_log=self._status.get('msg'),
                             exec_user=User.objects.get(pk=self.user_id)).save()
        except Exception as e:
            logger.exception(e)

    def run(self):
        if self.action_type == 'clone':
            self._clone()
        elif self.action_type == 'pull':
            self._pull()
        elif self.action_type == 'clean':
            self._clean()
        elif self.action_type == 'find':
            self._find()
        else:
            self._status['msg'] = 'Not support action type: {0}'.format(
                self.action_type)
        self._save_log()
        return self._status


@shared_task
def run_ansible_task(ansible_type, log_id, object_id, inventory_id,
                     config_id, user_id, **user_input):
    return Ansible(ansible_type, log_id, object_id, inventory_id,
                   config_id, user_id, **user_input).run()


@shared_task
def run_project_task(project_id, action_type, user_id):
    return Project(project_id, action_type, user_id).run()


@shared_task
def run_alert_task(alert_name, message):
    pass
