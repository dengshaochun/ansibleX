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


class GitProject(models.Model):

    project_id = models.UUIDField(_('project uuid'), default=uuid.uuid4())
    name = models.CharField(_('project name'), max_length=50)
    remote_url = models.URLField(_('project url'), unique=True)
    local_dir = models.CharField(_('project local dir'), max_length=100)
    auth_user = models.CharField(_('project auth user'),
                                 max_length=50, blank=True, null=True)
    auth_token = models.CharField(_('project auth token'), max_length=50,
                                  blank=True, null=True)
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
        return PrpCrypt().decrypt(self.auth_token) if self.auth_token else None

    @token.setter
    def token(self, value):
        if value:
            self.auth_token = PrpCrypt().encrypt(value)

    def delete(self, using=None, keep_parents=False):
        if os.path.exists(self.local_dir):
            shutil.rmtree(self.local_dir)
        super(GitProject, self).delete(using, keep_parents)


class ProjectActionLog(models.Model):
    ACTION_TYPES = (
        ('clone', 'clone'),
        ('pull', 'pull'),
        ('clean', 'clean'),
        ('find', 'find')
    )

    log_id = models.UUIDField(_('log uuid'), default=uuid.uuid4())
    project = models.ForeignKey('GitProject',
                                verbose_name=_('project'),
                                related_name='project_project_action_log',
                                on_delete=models.CASCADE)
    action_type = models.CharField(_('action type'), choices=ACTION_TYPES,
                                   max_length=20)
    action_status = models.BooleanField(_('action status'), default=True)
    action_log = models.TextField(_('action log'), blank=True, null=True)
    action_time = models.DateTimeField(_('action time'), auto_now=True)
    exec_user = models.ForeignKey(User,
                                  verbose_name=_('project'),
                                  related_name='user_project_action_log',
                                  on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '{0}'.format(self.log_id)
