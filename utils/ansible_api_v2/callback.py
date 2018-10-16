#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 10:17
# @Author  : Dengsc
# @Site    : 
# @File    : callback.py
# @Software: PyCharm


import json

from ansible import constants as C
from ansible.plugins.callback import CallbackBase
from ansible.plugins.callback.default import \
    CallbackModule as PlaybookCallBackBase


class AdHocResultCallback(CallbackBase):
    """
    Command result Callback
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'default'

    def __init__(self, display=None):
        self.result_q = dict(contacted={}, dark={})
        super(AdHocResultCallback, self).__init__(display)

    def gather_result(self, n, res):
        self.result_q[n].update({res._host.name: res._result})

    def v2_runner_on_ok(self, result):
        self.gather_result('contacted', result)

        for remove_key in ('invocation', '_ansible_parsed',
                           '_ansible_no_log', 'diff'):
            if remove_key in result._result:
                del result._result[remove_key]

        rc = result._result.get('rc')
        if rc is not None and result._result.get('stdout'):
            msg = "{host} | SUCCESS | rc={rc} >> \n{stdout}".format(
                host=result._host.get_name(),
                rc=rc,
                stdout=result._result.get('stdout'))
        else:
            msg = "{host} | SUCCESS >> \n{stdout}".format(
                host=result._host.get_name(),
                stdout=json.dumps(result._result, indent=4))
        self._display.display(msg, color=C.COLOR_OK)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.gather_result('dark', result)

        for remove_key in ('invocation', ):
            if remove_key in result._result:
                del result._result[remove_key]

        rc = result._result.get('rc')
        if rc is not None and result._result.get('stderr'):
            msg = "{host} | FAILED | rc={rc} >> \n{stdout}".format(
                host=result._host.get_name(),
                rc=result._result.get('rc'),
                stdout=result._result.get('stderr'))
        else:
            msg = "{host} | FAILED! >> {stdout}".format(
                host=result._host.get_name(),
                stdout=json.dumps(result._result, indent=4))
        self._display.display(msg, color=C.COLOR_ERROR)

    def v2_runner_on_unreachable(self, result):
        self.gather_result('contacted', result)

        for remove_key in ('invocation', ):
            if remove_key in result._result:
                del result._result[remove_key]

        msg = "{host} | UNREACHABLE! => {stdout}".format(
            host=result._host.get_name(),
            stdout=json.dumps(result._result, indent=4))
        self._display.display(msg, color=C.COLOR_ERROR)

    def v2_playbook_on_task_start(self, task, is_conditional):
        pass

    def v2_playbook_on_play_start(self, play):
        pass


class PlaybookResultCallBack(PlaybookCallBackBase):
    """
    Custom callback model for handlering the output data of
    execute playbook file,
    Base on the build-in callback plugins of ansible which named `json`.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'Dict'

    def __init__(self, display=None):

        super(PlaybookResultCallBack, self).__init__()
        self.results = []
        self.output = ''
        self._play = None
        self._last_task_banner = None
        self.item_results = {}  # {'host': []}
        self._display = display

    def _new_play(self, play):
        return {
            'play': {
                'name': play.name,
                'id': str(play._uuid)
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.get_name(),
            },
            'hosts': {}
        }

    def v2_playbook_on_no_hosts_matched(self):
        self.output = 'skipping: No match hosts.'
        super(PlaybookResultCallBack, self).v2_playbook_on_no_hosts_matched()

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

        super(PlaybookResultCallBack, self).v2_playbook_on_task_start(
            task,
            is_conditional)

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

        super(PlaybookResultCallBack, self).v2_playbook_on_play_start(play)

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        summary = {}
        for h in hosts:
            t = stats.summarize(h)
            summary[h] = t

        if self.output:
            pass
        else:
            self.output = {
                'plays': self.results,
                'stats': summary
            }
        super(PlaybookResultCallBack, self).v2_playbook_on_stats(stats)

    def gather_result(self, result):
        if result._task.loop and 'results' in result._result and result._host.name in self.item_results:
            result._result.update({
                'results': self.item_results[result._host.name]
            })
            del self.item_results[result._host.name]

        self.results[-1]['tasks'][-1]['hosts'][result._host.name] = result._result

    def gather_item_result(self, result):
        self.item_results.setdefault(result._host.name, []).append(result._result)

    def v2_runner_on_ok(self, result):
        if 'ansible_facts' in result._result:
            del result._result['ansible_facts']

        self.gather_result(result)

        super(PlaybookResultCallBack, self).v2_runner_on_ok(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.gather_result(result)

        super(PlaybookResultCallBack, self).v2_runner_on_failed(
            result,
            ignore_errors)

    def v2_runner_on_unreachable(self, result):
        self.gather_result(result)

        super(PlaybookResultCallBack, self).v2_runner_on_unreachable(result)

    def v2_runner_on_skipped(self, result):
        self.gather_result(result)

        super(PlaybookResultCallBack, self).v2_runner_on_skipped(result)

    def v2_runner_item_on_ok(self, result):
        self.gather_item_result(result)

        super(PlaybookResultCallBack, self).v2_runner_item_on_ok(result)

    def v2_runner_item_on_failed(self, result):
        self.gather_item_result(result)

        super(PlaybookResultCallBack, self).v2_runner_item_on_failed(result)

    def v2_runner_item_on_skipped(self, result):
        self.gather_item_result(result)

        super(PlaybookResultCallBack, self).v2_runner_item_on_skipped(result)
