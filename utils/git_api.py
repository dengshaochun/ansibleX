#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/29 20:50
# @Author  : Dengsc
# @Site    : 
# @File    : git_api.py
# @Software: PyCharm


import os
import git
from django.conf import settings


class GitUtil(object):

    def __init__(self, url, username=None, token=None):
        if username and token:
            self.remote_url = '{schema}{username}:{token}@{short_url}'.format(
                schema=url.split('//')[0] + '//',
                username=username,
                token=token,
                short_url=url.split('//')[1]
            )
        else:
            self.remote_url = url
        self.project_name = url.split('/')[-1].split('.')[0]
        self.local_path = os.path.join(settings.PROJECT_LOCAL_BASE_DIR,
                                       self.project_name)
        self._status = {
            'succeed': True,
            'msg': ''
        }

    def clone(self):
        try:
            repo = git.Repo.clone_from(
                self.remote_url,
                self.local_path, branch='master')
            version = repo.head.commit.hexsha
            self._status['etc'] = {
                'version': version
            }
            self._status['msg'] = 'Execute success! current version: {0}'.format(
                version)
        except Exception as e:
            self._status['succeed'] = False
            self._status['msg'] = str(e)

        return self._status

    def pull(self):

        try:
            repo = git.Repo(self.local_path)
            origin = repo.remotes[0]
            version = str(origin.pull()[0].commit)
            self._status['etc'] = {
                'version': version
            }
            self._status['msg'] = 'Execute success! current version: {0}'.format(
                version)
        except Exception as e:
            self._status['succeed'] = False
            self._status['msg'] = str(e)

        return self._status
