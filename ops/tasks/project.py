#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 15:50
# @Author  : Dengsc
# @Site    : 
# @File    : project.py
# @Software: PyCharm

import os
import shutil
import logging
from utils.git_api import GitUtil
from celery import shared_task
from ops.models import AnsiblePlayBook, ProjectTask, ProjectTaskLog


logger = logging.getLogger(__name__)


class Project(object):

    def __init__(self, task_id, celery_task_id):
        self._status = {
            'succeed': False,
            'msg': ''
        }

        self.task_id = task_id
        self.celery_task_id = celery_task_id
        self.task = ProjectTask.objects.get(task_id=task_id)
        self.action_type = self.task.action_type
        self.repo = None
        self.project = self.task.project
        self.log_instance = self._get_log_instance()
        if self.project and self.project.active:
            self.repo = GitUtil(self.project.remote_url,
                                self.project.project_id,
                                self.project.auth_user,
                                self.project.token)

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
                                    project=self.project,
                                    owner=self.task.owner).save()
                    _add += 1
                else:
                    _skip += 1
            self._status['succeed'] = True
            self._status['msg'] = 'playbook add {0}, skip {1}!'.format(
                _add, _skip)
        except Exception as e:
            self._status['msg'] = str(e)

    def _get_log_instance(self):
        try:
            log_instance = ProjectTaskLog(task=self.task,
                                          celery_task_id=self.celery_task_id)
            log_instance.save()
            return log_instance
        except Exception as e:
            logger.exception(e)
            return None

    def _save_log(self):
        if self.log_instance:
            self.log_instance.succeed = self._status.get('succeed', False)
            self.log_instance.task_log = self._status.get('msg', '')
            self.log_instance.save()
        else:
            logger.exception('Log instance is None!')

    def run(self):
        if self.action_type == 'clone':
            self._clone()
        elif self.action_type == 'pull':
            self._pull()
        elif self.action_type == 'clean':
            self._clean()
        elif self.action_type == 'find':
            self._find()
        elif self.action_type == 'hard_clone':
            self._clean()
            self._clone()
        else:
            self._status['msg'] = 'Not support action type: {0}'.format(
                self.action_type)
        self._save_log()
        return self._status


@shared_task
def run_project_task(task_id):
    return Project(task_id, celery_task_id=run_project_task.request.id).run()
