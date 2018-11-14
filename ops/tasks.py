#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 19:13
# @Author  : Dengsc
# @Site    : 
# @File    : tasks.py
# @Software: PyCharm

import os
import time
import json
import markdown
import requests
import shutil
import logging
import datetime
from django.core.mail import EmailMultiAlternatives
from utils.git_api import GitUtil
from celery import shared_task
from django.conf import settings
from utils.ansible_api_v2.runner import AdHocRunner, PlaybookRunner
from ops.models import (AnsiblePlayBook, AnsibleLock, AnsiblePlayBookTask,
                        AnsibleScriptTask, ProjectTask, Alert, AlertLog,
                        ProjectTaskLog, AnsibleScriptTaskLog,
                        AnsiblePlayBookTaskLog)
from utils.ansible_api_v2.display import MyDisplay
from utils.redis_api import RedisQueue

logger = logging.getLogger(__name__)


class Ansible(object):

    def __init__(self, ansible_type, task_id):

        self.ansible_type = ansible_type
        self.task_id = task_id
        self.task = None
        self.extra_vars = {}

        self.succeed = False
        self.result = None
        self.log_obj = None

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
                                               self.task.instance.object_id)

        self.runner = self._get_runner()

    def _get_runner(self):
        if self.ansible_type == 'script':
            runner = AdHocRunner(
                module_name=self.task.script.ansible_module.name,
                module_args=self.module_args,
                hosts=self.task.inventory.get_json_inventory(),
                log_path=self.log_path,
                log_id=self.task_id,
                **self.kwargs
            )
        else:
            runner = PlaybookRunner(
                playbook_path=self.task.playbook.file_path.path,
                hosts=self.task.inventory.get_json_inventory(),
                log_path=self.log_path,
                log_id=self.task_id,
                roles_path=self.task.playbook.role_path or None,
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

    def _save_log(self):
        try:
            # save log
            if self.ansible_type == 'script':
                self.log_obj = AnsibleScriptTaskLog(
                    task=self.task,
                    succeed=self.succeed)
            else:
                self.log_obj = AnsiblePlayBookTaskLog(
                    task=self.task,
                    succeed=self.succeed)
            self.log_obj.completed_log = self.result
            self.log_obj.save()
        except Exception as e:
            logger.exception(e)

    def _send_alert(self):

        markdown_template = '### Alert Information\n' + \
                            '- **Ansible Type**: {ansible_type}\n' + \
                            '- **Instance Name**: {instance_name}\n' + \
                            '- **Execute User**: {exec_user}\n' + \
                            '- **Detail Log**: [task log]({full_log})\n' + \
                            '- **Succeed**: {succeed}'

        # send alert
        if self.task.instance.alert:
            if self.task.instance.alert_succeed or \
                    self.task.instance.alert_failed:
                run_alert_task(
                    self.task.instance.alert.name,
                    markdown_template.format(
                        ansible_type=self.ansible_type,
                        instance_name=self.task.instance.name,
                        succeed=self.succeed,
                        exec_user=self.task.owner,
                        full_log='{0}{1}'.format(
                            settings.SERVER_BASE_URL,
                            self.log_obj.task_log.url)
                    )
                )

    def _run_end(self):
        self._release_lock()
        self._save_log()
        self._set_redis_expire()
        self._send_alert()


class Project(object):

    def __init__(self, task_id):
        self._status = {
            'succeed': False,
            'msg': ''
        }

        self.task_id = task_id
        self.task = ProjectTask.objects.get(task_id=task_id)
        self.action_type = self.task.action_type
        self.repo = None
        self.project = self.task.project
        if self.project and self.project.active:
            self.repo = GitUtil(self.project.remote_url,
                                self.project.project_id,
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
            ProjectTaskLog(task=self.task, succeed=self._status.get('succeed'),
                           task_log=self._status.get('result')).save()
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
        elif self.action_type == 're_clone':
            self._clean()
            self._clone()
        else:
            self._status['msg'] = 'Not support action type: {0}'.format(
                self.action_type)
        self._save_log()
        return self._status


class AlertSender(object):

    def __init__(self, alert_name, message):
        self.alert_obj = Alert.objects.get(name=alert_name)
        self.ding_talk = self.alert_obj.ding_talk
        self.email = self.alert_obj.email
        self.message = message
        self.alert_users = []
        self.subject = '[{0} Alert] - from devOps'.format(
            self.alert_obj.level.name)
        self.status = False
        self.html_message = markdown.markdown(message)

        self._get_alert_users()

    def _get_alert_users(self):
        for group in self.alert_obj.groups.all():
            for user in group.users.all():
                if user.profile.active:
                    self.alert_users.append(user.profile)

    def _send_email(self):
        email_users = [x.email for x in self.alert_users if x.email]
        msg = EmailMultiAlternatives(self.subject,
                                     'receive new alert',
                                     settings.EMAIL_FROM,
                                     email_users)
        msg.attach_alternative(self.html_message, 'text/html')
        msg.send()

    def _send_ding_talk(self):
        result = requests.post(
            url=self.ding_talk.url,
            headers={'Content-Type': 'application/json'},
            data=self._get_ding_talk_data()
        )
        result.raise_for_status()

    def _get_ding_talk_data(self):

        at_dict = {
            'atMobiles': None,
            'isAtAll': 'false'
        }

        text_dict = {
            'msgtype': 'text',
            'text': {
                'content': None
            },
            'at': None
        }

        markdown_dict = {
            'msgtype': 'markdown',
            'markdown': {
                'title': None,
                'text': None
            },
            'at': None
        }

        mobiles = [x.phone for x in self.alert_users if x.phone]
        at_content = '\n \n \n' + ' '.join(['@{0}'.format(x) for x in mobiles])
        at_dict['atMobiles'] = mobiles
        if self.ding_talk.at_all:
            at_dict['isAtAll'] = 'true'

        if self.ding_talk.msg_type == 'markdown':
            markdown_dict['markdown']['title'] = self.subject
            markdown_dict['markdown']['text'] = self.message + at_content
            content = markdown_dict
        else:
            text_dict['text']['content'] = self.html_message + at_content
            content = text_dict
        content['at'] = at_dict

        return json.dumps(content)

    def run(self):
        try:
            if self.email:
                self._send_email()
            if self.ding_talk:
                self._send_ding_talk()
            self.status = True
        except Exception as e:
            logger.exception(e)
            self.status = False
        finally:
            AlertLog(alert=self.alert_obj,
                     content=self.message, status=self.status).save()
        return self.status


@shared_task
def run_ansible_playbook_task(task_id):
    return Ansible(ansible_type='playbook', task_id=task_id).run()


@shared_task
def run_ansible_script_task(task_id):
    return Ansible(ansible_type='script', task_id=task_id).run()


@shared_task
def run_project_task(task_id):
    return Project(task_id).run()


@shared_task
def run_alert_task(alert_name, message):
    return AlertSender(alert_name, message).run()
