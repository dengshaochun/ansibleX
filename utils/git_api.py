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

    def __init__(self, url, username, token):
        self.remote_url = '{schema}{username}:{token}@{short_url}'.format(
            schema=url.split('//')[0] + '//',
            username=username,
            token=token,
            short_url=url.split('//')[1]
        )
        self.project_name = url.split('/')[-1].split('.')[0]
        self.local_path = os.path.join(settings.PROJECT_LOCAL_BASE_DIR,
                                       self.project_name)

    def clone(self):
        _status = {
            'succeed': True,
            'msg': 'operation success!'
        }
        try:
            repo = git.Repo.clone_from(
                self.remote_url,
                self.local_path, branch='master')
            _status['etc'] = {
                'version': repo.head.commit.hexsha
            }
            return _status
        except Exception as e:
            _status['succeed'] = False
            _status['msg'] = str(e)
            return _status

    def pull(self):
        _status = {
            'succeed': True,
            'msg': 'operation success!'
        }
        try:
            repo = git.Repo(self.local_path)
            origin = repo.remotes[0]
            version = str(origin.pull()[0].commit)
            _status['etc'] = {
                'version': version
            }
        except Exception as e:
            _status['succeed'] = False
            _status['msg'] = str(e)

        return _status
