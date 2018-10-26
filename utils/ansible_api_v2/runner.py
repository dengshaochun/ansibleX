#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 10:17
# @Author  : Dengsc
# @Site    : 
# @File    : runner.py
# @Software: PyCharm


import os
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
import ansible.constants as C
from ansible.utils.vars import load_extra_vars
from ansible.utils.vars import load_options_vars
from ansible.errors import AnsibleError

from utils.ansible_api_v2.inventory import MyInventory
from utils.ansible_api_v2.executor import MyPlaybookExecutor, MyTaskQueueManager
from utils.ansible_api_v2.callback import (PlaybookResultCallBack,
                                           AdHocResultCallback)
from utils.ansible_api_v2.display import MyDisplay


__all__ = ['AdHocRunner', 'PlayBookRunner']
C.HOST_KEY_CHECKING = False


class PlaybookRunner(object):
    """
    The plabybook API.
    """

    Options = namedtuple('Options', [
        'listtags', 'listtasks', 'listhosts', 'syntax', 'connection',
        'module_path', 'forks', 'remote_user', 'private_key_file', 'timeout',
        'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
        'scp_extra_args', 'become', 'become_method', 'become_user',
        'verbosity', 'check', 'extra_vars', 'diff', 'roles_path'])

    def __init__(
        self,
        hosts=None,
        playbook_path=None,
        log_path=None,
        log_id=None,
        **kwargs
    ):

        self.pattern = kwargs.get('pattern', 'all')
        C.RETRY_FILES_ENABLED = False
        display = MyDisplay(log_id=log_id, log_path=log_path)
        self.callback_module = PlaybookResultCallBack(display=display)
        if playbook_path is None or not os.path.exists(playbook_path):
            raise AnsibleError(
                'Not Found the playbook file: %s.' % playbook_path)
        self.playbook_path = playbook_path
        self.inventory = MyInventory(hosts_list=hosts)
        self.loader = DataLoader()
        self.variable_manager = VariableManager(self.loader, self.inventory)
        self.passwords = kwargs.get('passwords', {})

        self.options = self.Options(
            listtags=kwargs.get('listtags', False),
            listtasks=kwargs.get('listtasks', False),
            listhosts=kwargs.get('listhosts', False),
            syntax=kwargs.get('syntax', False),
            ssh_common_args=kwargs.get('ssh_common_args', None),
            ssh_extra_args=kwargs.get('ssh_extra_args', None),
            sftp_extra_args=kwargs.get('sftp_extra_args', None),
            scp_extra_args=kwargs.get('scp_extra_args', None),
            connection=kwargs.get('connection_type', 'smart'),
            timeout=kwargs.get('timeout', 60),
            module_path=kwargs.get('module_path', None),
            forks=kwargs.get('forks', 5),
            become=kwargs.get('become', False),
            become_method=kwargs.get('become_method', 'sudo'),
            become_user=kwargs.get('become_user', None),
            check=kwargs.get('check', False),
            remote_user=kwargs.get('remote_user', None),
            verbosity=kwargs.get('verbosity', None),
            extra_vars=kwargs.get('extra_vars', []),
            private_key_file=kwargs.get('private_key_file', None),
            diff=kwargs.get('diff', False),
            roles_path=kwargs.get('roles_path', None)
        )

        self.variable_manager.extra_vars = load_extra_vars(loader=self.loader,
                                                           options=self.options)
        self.variable_manager.options_vars = load_options_vars(self.options, '')

        self.variable_manager.set_inventory(self.inventory)
        self.runner = MyPlaybookExecutor(
            playbooks=[self.playbook_path],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.passwords,
        )
        if self.runner._tqm:
            self.runner._tqm._stdout_callback = self.callback_module

    def run(self):

        succeed = True
        if not self.inventory.list_hosts('all'):
            raise AnsibleError('Inventory is empty.')

        self.runner.run()
        self.runner._tqm.cleanup()
        if isinstance(self.callback_module.output, str):
            raise AnsibleError(self.callback_module.output)
        elif isinstance(self.callback_module.output, dict):
            stats = self.callback_module.output.get('stats')
            if stats and isinstance(stats, dict):
                for k, v in stats.items():
                    if v and v.get('failures') > 0 or v.get('unreachable') > 0:
                        succeed = False
        return succeed, self.callback_module.output


class AdHocRunner(object):

    Options = namedtuple('Options', [
        'connection', 'module_path', 'private_key_file', 'remote_user',
        'timeout', 'forks', 'become', 'become_method', 'become_user', 'check',
        'extra_vars', 'diff', 'verbosity'
    ])

    def __init__(
            self,
            hosts='',
            module_name='command',
            module_args='',
            log_path=None,
            log_id=None,
            **kwargs
    ):

        # storage & defaults
        self.pattern = kwargs.get('pattern', 'all')
        self.loader = DataLoader()
        self.module_name = module_name
        self.module_args = module_args
        self.check_module_args()
        self.gather_facts = 'no'
        display = MyDisplay(log_id=log_id, log_path=log_path)
        self.callback_module = AdHocResultCallback(display=display)
        self.options = self.Options(
            connection=kwargs.get('connection_type', 'smart'),
            timeout=kwargs.get('timeout', 60),
            module_path=kwargs.get('module_path', None),
            forks=kwargs.get('forks', 5),
            become=kwargs.get('become', False),
            become_method=kwargs.get('become_method', 'sudo'),
            become_user=kwargs.get('become_user', None),
            check=kwargs.get('check', False),
            remote_user=kwargs.get('remote_user', None),
            verbosity=kwargs.get('verbosity', None),
            extra_vars=kwargs.get('extra_vars', []),
            private_key_file=kwargs.get('private_key_file', None),
            diff=kwargs.get('diff', False)
        )

        self.inventory = MyInventory(hosts_list=hosts)
        self.variable_manager = VariableManager(self.loader, self.inventory)
        self.variable_manager.extra_vars = load_extra_vars(loader=self.loader,
                                                           options=self.options)
        self.variable_manager.options_vars = load_options_vars(self.options, '')
        self.passwords = kwargs.get('passwords', {})

        self.play_source = dict(
            name='Ansible Ad-hoc',
            hosts=self.pattern,
            gather_facts=self.gather_facts,
            tasks=[dict(action=dict(
                module=self.module_name,
                args=self.module_args))]
        )

        self.play = Play().load(
            self.play_source, variable_manager=self.variable_manager,
            loader=self.loader)

        self.runner = MyTaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.passwords,
            stdout_callback=self.callback_module
        )

        # ** end __init__() **

    def run(self):

        succeed = True
        if not self.inventory.list_hosts('all'):
            raise AnsibleError('Inventory is empty.')

        if not self.inventory.list_hosts(self.pattern):
            raise AnsibleError(
                'pattern: %s  dose not match any hosts.' % self.pattern)

        try:
            self.runner.run(self.play)
        finally:
            if self.runner:
                self.runner.cleanup()
            if self.loader:
                self.loader.cleanup_all_tmp_files()

        if isinstance(self.callback_module.result_q, str):
            raise AnsibleError(self.callback_module.result_q)
        elif isinstance(self.callback_module.result_q, dict):
            if len(self.callback_module.result_q.get('dark')) > 0:
                succeed = False

        return succeed, self.callback_module.result_q

    def check_module_args(self):
        if self.module_name in C.MODULE_REQUIRE_ARGS and not self.module_args:
            err = 'No argument passed to \'%s\' module.' % self.module_name
            raise AnsibleError(err)


if __name__ == '__main__':
    pass
