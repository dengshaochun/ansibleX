#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 15:49
# @Author  : Dengsc
# @Site    : 
# @File    : ansible.py
# @Software: PyCharm


import os
import time
import logging
import datetime
from celery import shared_task
from django.conf import settings
from utils.ansible_api_v2.runner import AdHocRunner, PlaybookRunner
from ops.models import (AnsibleLock, AnsiblePlayBookTask,
                        AnsibleScriptTask,
                        AnsibleScriptTaskLog,
                        AnsiblePlayBookTaskLog)
from utils.ansible_api_v2.display import MyDisplay
from ops.tasks.alert import run_alert_task
from utils.redis_api import RedisQueue

logger = logging.getLogger(__name__)


class Ansible(object):

    def __init__(self, ansible_type, task_id, celery_task_id):

        self.ansible_type = ansible_type
        self.task_id = task_id
        self.celery_task_id = celery_task_id
        self.task = None
        self.extra_vars = {}

        self.succeed = False
        self.result = None

        # current year and month
        yy_mm = datetime.datetime.now().strftime('%Y%m')
        # define log path
        self.log_path = os.path.join(settings.ANSIBLE_BASE_LOG_DIR,
                                     yy_mm, self.task_id)
        # define ansible display
        self.display = MyDisplay(log_id=self.task_id, log_path=self.log_path)

        # get ansible instance
        if self.ansible_type == 'script':
            self.task = AnsibleScriptTask.objects.get(task_id=task_id)
            self.user_raw = self.task.get_json_user_input()
            if self.user_raw.get('module_args'):
                self.module_args = self.user_raw.get('module_args')
            else:
                self.module_args = self.task.instance.module_args
        elif self.ansible_type == 'playbook':
            self.task = AnsiblePlayBookTask.objects.get(task_id=self.task_id)
            self.user_raw = self.task.get_json_user_input()
        else:
            raise Exception('Not support ansible type: {0} !'.format(
                self.ansible_type))

        self.extra_vars = self.task.instance.get_json_extra_vars()

        if self.user_raw.get('extra_vars'):
            self.extra_vars.update(self.user_raw.get('extra_vars'))

        self.kwargs = self.task.config.get_json_config()
        self.kwargs['extra_vars'] = [self.extra_vars, ]

        self.lock_object_id = '{0}-{1}'.format(self.ansible_type,
                                               self.task.instance.instance_id)

        self.log_instance = self._get_log_instance()
        self.runner = self._get_runner()

    def _get_runner(self):
        if self.ansible_type == 'script':
            runner = AdHocRunner(
                module_name=self.task.instance.ansible_module.name,
                module_args=self.module_args,
                hosts=self.task.inventory.get_json_inventory(),
                log_path=self.log_path,
                log_id=self.task_id,
                **self.kwargs
            )
        else:
            runner = PlaybookRunner(
                playbook_path=self.task.instance.file_path.path,
                hosts=self.task.inventory.get_json_inventory(),
                log_path=self.log_path,
                log_id=self.task_id,
                roles_path=self.task.instance.role_path or None,
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
        if not self.task.instance.concurrent:
            while True:
                lock = AnsibleLock.objects.filter(
                    lock_object_id=self.lock_object_id).first()
                if not lock:
                    break
                self.display.display(
                    'Another same {0} is running, waiting...'.format(
                        self.ansible_type))
                time.sleep(10)

            AnsibleLock(lock_object_id=self.lock_object_id).save()
        self.display.display(settings.ANSIBLE_TASK_START_PREFIX)

    def _release_lock(self):
        try:
            # release lock
            lock = AnsibleLock.objects.filter(
                lock_object_id=self.lock_object_id).first()
            if lock:
                lock.delete()
            self.display.display(settings.ANSIBLE_TASK_END_PREFIX)
        except Exception as e:
            logger.exception(e)

    def _set_redis_expire(self):
        self.redis = RedisQueue(name=self.task_id)
        self.redis.expire(settings.ANSIBLE_RESULT_CACHE_EXPIRE)

    def _get_log_instance(self):
        log_instance = None
        try:
            # get log instance
            if self.ansible_type == 'script':
                log_instance = AnsibleScriptTaskLog(
                    task=self.task,
                    celery_task_id=self.celery_task_id)
            else:
                log_instance = AnsiblePlayBookTaskLog(
                    task=self.task,
                    celery_task_id=self.celery_task_id)
            log_instance.save()
        except Exception as e:
            logger.exception(e)
        return log_instance

    def _update_task_log(self):
        if self.log_instance:
            self.log_instance.succeed = self.succeed
            self.log_instance.completed_log = self.result
            self.log_instance.save()
        else:
            logger.exception('log instance is None!')

    def _send_alert(self):

        markdown_template = '### Alert Information\n' + \
                            '- **Ansible Type**: {ansible_type}\n' + \
                            '- **Instance Name**: {instance_name}\n' + \
                            '- **Execute User**: {exec_user}\n' + \
                            '- **Detail Log**: [task log]({full_log})\n' + \
                            '- **Succeed**: {succeed}'

        message = markdown_template.format(
            ansible_type=self.ansible_type,
            instance_name=self.task.instance.name,
            succeed=self.succeed,
            exec_user=self.task.owner,
            full_log='{0}{1}'.format(
                settings.SERVER_BASE_URL,
                self.log_instance.task_log.url)
        )
        # send alert
        if self.task.instance.alert:
            if (self.task.instance.alert_succeed and self.succeed) or \
                    (self.task.instance.alert_failed and not self.succeed):
                run_alert_task(
                    self.task.instance.alert.name,
                    message=message
                )

    def _run_end(self):
        self._release_lock()
        self._update_task_log()
        self._set_redis_expire()
        self._send_alert()


@shared_task
def run_ansible_playbook_task(task_id):
    return Ansible(ansible_type='playbook', task_id=task_id,
                   celery_task_id=run_ansible_playbook_task.request.id
                   ).run()


@shared_task
def run_ansible_script_task(task_id):
    return Ansible(ansible_type='script', task_id=task_id,
                   celery_task_id=run_ansible_script_task.request.id
                   ).run()
