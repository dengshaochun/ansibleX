#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/29 16:39
# @Author  : Dengsc
# @Site    : 
# @File    : proj.py
# @Software: PyCharm


import os
import uuid
import shutil
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from utils.encrypt import PrpCrypt
from utils.git_api import GitUtil


class GitProject(models.Model):

    project_id = models.UUIDField(_('project uuid'), default=uuid.uuid4())
    name = models.CharField(_('project name'), max_length=50)
    remote_url = models.URLField(_('project url'))
    local_dir = models.CharField(_('project local dir'), max_length=100)
    auth_user = models.CharField(_('project auth user'), max_length=50)
    auth_token = models.CharField(_('project auth token'), max_length=50)
    current_version = models.CharField(_('current version'), max_length=50)
    active = models.BooleanField(_('active status'), default=True)
    last_update_time = models.DateTimeField(_('last update time'),
                                            auto_now_add=True)
    owner = models.ForeignKey(User, verbose_name=_('project owner'),
                              on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    @property
    def token(self):
        return PrpCrypt().decrypt(self.auth_token)

    @token.setter
    def token(self, token):
        self.auth_token = PrpCrypt().encrypt(token)

    def do_clean_local_path(self):
        _status = {
            'succeed': False,
            'msg': ''
        }
        if self.local_dir:
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir)
                _status['succeed'] = True
                _status['msg'] = 'Remove local path : {0} successful!'.format(
                    self.local_dir)
            else:
                _status['msg'] = 'Local path: {0} do not exists!'.format(
                    self.local_dir)
        else:
            _status['msg'] = 'local_dir field is null!'
        return _status

    def do_project_action(self, action):
        _status = {
            'succeed': False,
            'msg': ''
        }
        if not self.active:
            _status['msg'] = 'Project is inactive! Action canceled!'
        else:
            repo = GitUtil(self.remote_url, self.auth_user,
                           self.token)
            if action == 'clone':
                result = repo.clone()
                self.local_dir = repo.local_path
            elif action == 'pull':
                result = repo.pull()
            else:
                _status['msg'] = 'Not supported Action [{0}]!'.format(action)
                result = {}
            if result.get('succeed'):
                self.current_version = result.get('etc', {}).get('version')
                self.save()
            ProjectActionLog(action_type=action,
                             action_status=result.get('succeed'),
                             project=self,
                             action_log=result.get('msg')).save()
            _status['succeed'] = result.get('succeed')
            _status['msg'] = result.get('msg')
        return _status

    def find_playbooks(self, owner):

        _status = {
            'succeed': False,
            'msg': ''
        }
        _add = 0
        _skip = 0
        try:
            playbook_path = os.path.join(self.local_dir, 'playbooks')
            role_path = os.path.join(self.local_dir, 'roles')
            playbooks = os.listdir(playbook_path)
            for playbook in playbooks:
                if playbook.endswith('.yml'):
                    from ops.models.ansible import AnsiblePlayBook
                    obj = AnsiblePlayBook.objects.filter(
                        name=playbook,
                        project=self
                    ).first()
                    if not obj:
                        AnsiblePlayBook(name=playbook,
                                        file_path=os.path.join(playbook_path,
                                                               playbook),
                                        role_path=role_path,
                                        owner=owner,
                                        project=self).save()
                        _add += 1
                    else:
                        _skip += 1
            _status['succeed'] = True
            _status['msg'] = 'New add {0}, Skip {1}!'.format(_add, _skip)
        except Exception as e:
            _status['msg'] = str(e)
        return _status


class ProjectActionLog(models.Model):
    ACTION_TYPES = (
        ('clone', 'clone'),
        ('pull', 'pull')
    )

    log_id = models.UUIDField(_('log uuid'), default=uuid.uuid4())
    project = models.ForeignKey('GitProject', verbose_name=_('project'),
                                on_delete=models.CASCADE)
    action_type = models.CharField(_('action type'), choices=ACTION_TYPES,
                                   max_length=20)
    action_status = models.BooleanField(_('action status'), default=True)
    action_log = models.TextField(_('action log'), blank=True, null=True)
    action_time = models.DateTimeField(_('action time'), auto_now=True)

    def __str__(self):
        return '{0}'.format(self.log_id)
