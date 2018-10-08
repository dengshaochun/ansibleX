#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 10:17
# @Author  : Dengsc
# @Site    : 
# @File    : callback.py
# @Software: PyCharm


import json

from ansible import constants as C
from ansible.utils.color import colorize, hostcolor
from ansible.plugins.callback import CallbackBase
from ansible.plugins.callback.default import \
    CallbackBase as playbook_CallBackBase
from ansible.playbook.task_include import TaskInclude


class CommandResultCallback(CallbackBase):
    """
    Command result Callback
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'default'

    def __init__(self, display=None):
        self.result_q = dict(contacted={}, dark={})
        super(CommandResultCallback, self).__init__(display)

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
        self.gather_result('dark', result)

        for remove_key in ('invocation', ):
            if remove_key in result._result:
                del result._result[remove_key]

        msg = "{host} | UNREACHABLE! => {stdout}".format(
            host=result._host.get_name(),
            stdout=json.dumps(result._result, indent=4))
        self._display.display(msg, color=C.COLOR_ERROR)


class AdHocResultCallback(CallbackBase):
    """
    AdHoc result Callback
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

        delegated_vars = result._result.get('_ansible_delegated_vars', None)

        if isinstance(result._task, TaskInclude):
            return
        elif result._result.get('changed', False):
            if delegated_vars:
                msg = "changed: [%s -> %s]" % (
                result._host.get_name(), delegated_vars['ansible_host'])
            else:
                msg = "changed: [%s]" % result._host.get_name()
            color = C.COLOR_CHANGED
        else:
            if delegated_vars:
                msg = "ok: [%s -> %s]" % (
                result._host.get_name(), delegated_vars['ansible_host'])
            else:
                msg = "ok: [%s]" % result._host.get_name()
            color = C.COLOR_OK

        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)
        else:
            self._clean_results(result._result, result._task.action)

            if (self._display.verbosity > 0
                or '_ansible_verbose_always' in result._result) \
                    and '_ansible_verbose_override' not in result._result:
                msg += " => %s" % (self._dump_results(result._result),)
            self._display.display(msg, color=color)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.gather_result('dark', result)
        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)

        self._handle_exception(result._result)
        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)

        else:
            if delegated_vars:
                self._display.display("fatal: [%s -> %s]: FAILED! => %s" % (
                result._host.get_name(), delegated_vars['ansible_host'],
                self._dump_results(result._result)), color=C.COLOR_ERROR)
            else:
                self._display.display("fatal: [%s]: FAILED! => %s" % (
                result._host.get_name(), self._dump_results(result._result)),
                                      color=C.COLOR_ERROR)

        if ignore_errors:
            self._display.display("...ignoring", color=C.COLOR_SKIP)

    def v2_runner_on_unreachable(self, result):
        self.gather_result('dark', result)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        if delegated_vars:
            self._display.display("fatal: [%s -> %s]: UNREACHABLE! => %s" % (
                result._host.get_name(), delegated_vars['ansible_host'],
                self._dump_results(result._result)),
                                  color=C.COLOR_UNREACHABLE)
        else:
            self._display.display("fatal: [%s]: UNREACHABLE! => %s" % (
                result._host.get_name(), self._dump_results(result._result)),
                                  color=C.COLOR_UNREACHABLE)

    def v2_runner_on_skipped(self, result):
        self.gather_result('dark', result)

        if self._plugin_options.get('show_skipped_hosts',
                                    C.DISPLAY_SKIPPED_HOSTS):

            self._clean_results(result._result, result._task.action)

            if result._task.loop and 'results' in result._result:
                self._process_items(result)
            else:
                msg = "skipping: [%s]" % result._host.get_name()
                if (self._display.verbosity > 0
                    or '_ansible_verbose_always' in result._result) \
                        and '_ansible_verbose_override' not in result._result:
                    msg += " => %s" % self._dump_results(result._result)
                self._display.display(msg, color=C.COLOR_SKIP)

    def v2_playbook_on_task_start(self, task, is_conditional):
        pass

    def v2_playbook_on_play_start(self, play):
        pass


class PlaybookResultCallBack(playbook_CallBackBase):
    """
    Custom callback model for handlering the output data of
    execute playbook file,
    Base on the build-in callback plugins of ansible which named `json`.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'Dict'

    def __init__(self, display=None):
        super(PlaybookResultCallBack, self).__init__(display)
        self.results = []
        self.output = ''
        self._play = None
        self._last_task_banner = None
        self.item_results = {}  # {'host': []}

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

    def _print_task_banner(self, task):
        # copy from default
        args = ''
        if not task.no_log and C.DISPLAY_ARGS_TO_STDOUT:
            args = u', '.join(u'%s=%s' % a for a in task.args.items())
            args = u' %s' % args

        self._display.banner(u"TASK [%s%s]" % (task.get_name().strip(), args))
        if self._display.verbosity >= 2:
            path = task.get_path()
            if path:
                self._display.display(u"task path: %s" % path, color=C.COLOR_DEBUG)

        self._last_task_banner = task._uuid

    def v2_playbook_on_no_hosts_matched(self):
        self.output = 'skipping: No match hosts.'
        self._display.display("skipping: no hosts matched", color=C.COLOR_SKIP)

    def v2_playbook_on_no_hosts_remaining(self):
        self._display.banner("NO MORE HOSTS LEFT")

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

        if self._play.strategy != 'free':
            self._print_task_banner(task)

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name

        self._play = play

        self._display.banner(msg)

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        summary = {}
        for h in hosts:
            t = stats.summarize(h)
            summary[h] = t
            self._display.display(u"%s : %s %s %s %s" % (
                hostcolor(h, t),
                colorize(u'ok', t['ok'], C.COLOR_OK),
                colorize(u'changed', t['changed'], C.COLOR_CHANGED),
                colorize(u'unreachable', t['unreachable'], C.COLOR_UNREACHABLE),
                colorize(u'failed', t['failures'], C.COLOR_ERROR)),
                                  screen_only=True
                                  )

            self._display.display(u"%s : %s %s %s %s" % (
                hostcolor(h, t, False),
                colorize(u'ok', t['ok'], None),
                colorize(u'changed', t['changed'], None),
                colorize(u'unreachable', t['unreachable'], None),
                colorize(u'failed', t['failures'], None)),
                                  log_only=True
                                  )

        self._display.display("", screen_only=True)

        # print custom stats
        if self._plugin_options.get('show_custom_stats',
                                    C.SHOW_CUSTOM_STATS) and stats.custom:
            self._display.banner("CUSTOM STATS: ")
            # per host
            # TODO: come up with 'pretty format'
            for k in sorted(stats.custom.keys()):
                if k == '_run':
                    continue
                self._display.display('\t%s: %s' % (k, self._dump_results(
                    stats.custom[k], indent=1).replace('\n', '')))

            # print per run custom stats
            if '_run' in stats.custom:
                self._display.display("", screen_only=True)
                self._display.display(
                    '\tRUN: %s' % self._dump_results(stats.custom['_run'],
                                                     indent=1).replace('\n',
                                                                       ''))
            self._display.display("", screen_only=True)

        if self.output:
            pass
        else:
            self.output = {
                'plays': self.results,
                'stats': summary
            }

    def gather_result(self, result):
        if result._task.loop and 'results' in \
                result._result and result._host.name in self.item_results:
            result._result.update({'results': self.item_results[result._host.name]})
            del self.item_results[result._host.name]

        self.results[-1]['tasks'][-1]['hosts'][result._host.name] = result._result

    def v2_runner_on_ok(self, result, **kwargs):
        if 'ansible_facts' in result._result:
            del result._result['ansible_facts']

        self.gather_result(result)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)

        if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        if isinstance(result._task, TaskInclude):
            return
        elif result._result.get('changed', False):
            if delegated_vars:
                msg = "changed: [%s -> %s]" % (
                result._host.get_name(), delegated_vars['ansible_host'])
            else:
                msg = "changed: [%s]" % result._host.get_name()
            color = C.COLOR_CHANGED
        else:
            if delegated_vars:
                msg = "ok: [%s -> %s]" % (
                result._host.get_name(), delegated_vars['ansible_host'])
            else:
                msg = "ok: [%s]" % result._host.get_name()
            color = C.COLOR_OK

        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)
        else:
            self._clean_results(result._result, result._task.action)

            if (self._display.verbosity > 0
                or '_ansible_verbose_always' in result._result) \
                    and '_ansible_verbose_override' not in result._result:
                msg += " => %s" % (self._dump_results(result._result),)
            self._display.display(msg, color=color)

    def v2_runner_on_failed(self, result, **kwargs):
        self.gather_result(result)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)

        if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        self._handle_exception(result._result)
        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)

        else:
            if delegated_vars:
                self._display.display("fatal: [%s -> %s]: FAILED! => %s" % (
                result._host.get_name(), delegated_vars['ansible_host'],
                self._dump_results(result._result)), color=C.COLOR_ERROR)
            else:
                self._display.display("fatal: [%s]: FAILED! => %s" % (
                result._host.get_name(), self._dump_results(result._result)),
                                      color=C.COLOR_ERROR)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.gather_result(result)

        if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        if delegated_vars:
            self._display.display("fatal: [%s -> %s]: UNREACHABLE! => %s" % (
                result._host.get_name(), delegated_vars['ansible_host'],
                self._dump_results(result._result)),
                                  color=C.COLOR_UNREACHABLE)
        else:
            self._display.display("fatal: [%s]: UNREACHABLE! => %s" % (
                result._host.get_name(), self._dump_results(result._result)),
                                  color=C.COLOR_UNREACHABLE)

    def v2_runner_on_skipped(self, result, **kwargs):
        self.gather_result(result)

        if self._plugin_options.get('show_skipped_hosts',
                                    C.DISPLAY_SKIPPED_HOSTS):

            self._clean_results(result._result, result._task.action)

            if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            if result._task.loop and 'results' in result._result:
                self._process_items(result)
            else:
                msg = "skipping: [%s]" % result._host.get_name()
                if (self._display.verbosity > 0
                    or '_ansible_verbose_always' in result._result) \
                        and '_ansible_verbose_override' not in result._result:
                    msg += " => %s" % self._dump_results(result._result)
                self._display.display(msg, color=C.COLOR_SKIP)

    def gather_item_result(self, result):
        self.item_results.setdefault(result._host.name, []).append(result._result)

    def v2_runner_item_on_ok(self, result):
        self.gather_item_result(result)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)
        if isinstance(result._task, TaskInclude):
            return
        elif result._result.get('changed', False):
            msg = 'changed'
            color = C.COLOR_CHANGED
        else:
            msg = 'ok'
            color = C.COLOR_OK

        if delegated_vars:
            msg += ": [%s -> %s]" % (
            result._host.get_name(), delegated_vars['ansible_host'])
        else:
            msg += ": [%s]" % result._host.get_name()

        msg += " => (item=%s)" % (self._get_item_label(result._result),)

        if (self._display.verbosity > 0
            or '_ansible_verbose_always' in result._result) \
                and '_ansible_verbose_override' not in result._result:
            msg += " => %s" % self._dump_results(result._result)
        self._display.display(msg, color=color)

    def v2_runner_item_on_failed(self, result):
        self.gather_item_result(result)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)
        self._handle_exception(result._result)

        msg = "failed: "
        if delegated_vars:
            msg += "[%s -> %s]" % (
            result._host.get_name(), delegated_vars['ansible_host'])
        else:
            msg += "[%s]" % (result._host.get_name())

        self._handle_warnings(result._result)
        self._display.display(msg + " (item=%s) => %s" % (
        self._get_item_label(result._result),
        self._dump_results(result._result)), color=C.COLOR_ERROR)

    def v2_runner_item_on_skipped(self, result):
        self.gather_item_result(result)

        if self._plugin_options.get('show_skipped_hosts',
                                    C.DISPLAY_SKIPPED_HOSTS):
            self._clean_results(result._result, result._task.action)
            msg = "skipping: [%s] => (item=%s) " % (
                result._host.get_name(),
                self._get_item_label(result._result))
            if (self._display.verbosity > 0
                or '_ansible_verbose_always' in result._result) \
                    and '_ansible_verbose_override' not in result._result:
                msg += " => %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_SKIP)
