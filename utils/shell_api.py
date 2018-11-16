#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 20:17
# @Author  : Dengsc
# @Site    : 
# @File    : shell_api.py
# @Software: PyCharm

import logging
import subprocess


logger = logging.getLogger(__name__)


def run_shell(command):
    """
    exec shell command
    :param command: shell scripts
    :return: stdout
    """

    _status = {
        'succeed': False,
        'result': None
    }

    try:
        logger.info('start run shell command: {0}'.format(command))
        child = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        result = [k for k in child.communicate() if k]
        _status['succeed'] = True
        _status['result'] = result
        return _status
    except Exception as e:
        logger.error('failed to run shell command: {0}'.format(command))
        logger.exception(e)
        _status['result'] = str(e)
        return _status
