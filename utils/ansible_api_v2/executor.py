#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 10:19
# @Author  : Dengsc
# @Site    : 
# @File    : executor.py
# @Software: PyCharm


import multiprocessing
import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.ssh_functions import check_for_controlpersist


class MyTaskQueueManager(TaskQueueManager):
    def _initialize_processes(self, num):
        self._workers = []
        current_process = multiprocessing.current_process
        current_process().daemon = False
        for i in range(num):
            rslt_q = multiprocessing.Queue()
            self._workers.append([None, rslt_q])


class MyPlaybookExecutor(PlaybookExecutor):

    def __init__(self, playbooks, inventory, variable_manager, loader,
                 options, passwords):
        super(MyPlaybookExecutor, self).__init__(playbooks, inventory,
                                                 variable_manager,
                                                 loader, options, passwords)

        self._playbooks = playbooks
        self._inventory = inventory
        self._variable_manager = variable_manager
        self._loader = loader
        self._options = options
        self.passwords = passwords
        self._unreachable_hosts = dict()

        if options.listhosts or options.listtasks \
                or options.listtags or options.syntax:
            self._tqm = None
        else:
            self._tqm = MyTaskQueueManager(inventory=inventory,
                                           variable_manager=variable_manager,
                                           loader=loader,
                                           options=options,
                                           passwords=self.passwords)

        # Note: We run this here to cache whether the default ansible ssh
        # executable supports control persist.  Sometime in the future we may
        # need to enhance this to check that ansible_ssh_executable specified
        # in inventory is also cached.  We can't do this caching at the point
        # where it is used (in task_executor) because that is post-fork and
        # therefore would be discarded after every task.
        check_for_controlpersist(C.ANSIBLE_SSH_EXECUTABLE)
