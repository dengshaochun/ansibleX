#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:25
# @Author  : Dengsc
# @Site    : 
# @File    : kadmin_api.py
# @Software: PyCharm


import os
import time
import filecmp
import kadmin
import logging
import datetime
from utils.shell_api import run_shell

logger = logging.getLogger(__name__)


class Kadmin(object):
    """
    kadmin operation
    """

    def __init__(self, admin_principal, admin_password, admin_keytab,
                 config, realms):
        """
        init kadmin object
        :param admin_principal: <str> admin username
        :param admin_password: <str> admin password
        :param admin_keytab: <str> admin keytab path
        :param config: <str> admin config path
        :param realms: <str> kdc realms
        """

        self.realms = realms
        self.config = config

        if not self._setup_config():
            raise Exception('Setup krb5.conf failed!')

        if admin_password:
            self.admin = kadmin.init_with_password(
                admin_principal, admin_password)
            self.shell = 'kadmin -p {0} -w {1} -q'.format(admin_principal,
                                                          admin_password)
        else:
            self.admin = kadmin.init_with_keytab(
                admin_principal, admin_keytab)
            self.shell = 'kadmin -p {0} -kt {1} -q'.format(admin_principal,
                                                           admin_keytab)

    def _setup_config(self):
        """
        copy krb5.conf /etc/ directory
        :return: <bool> status
        """

        # Todo make sure only one instance
        while os.path.exists('/etc/krb5.conf'):
            if filecmp.cmp('/etc/krb5.conf', self.config):
                return True
            logger.warning('Anothor kadmin instance exists!')
            time.sleep(5)

        if os.path.isfile(self.config):
            result = run_shell('sudo cp {0} /etc/'.format(self.config))
            return result.get('succeed')
        return False

    def _kadmin_shell(self, cmd):
        result = run_shell('{0} "{1}"'.format(self.shell, cmd))
        return result

    def add_principal(self, user):
        """
        add principal
        :param user: <str> username
        :return: <dict> principal information
        """
        if not self.get_principal_info(user):
            self.admin.addprinc(user)
        self.activate_principal(user)
        return self.get_principal_info(user)

    def expire_principal(self, user):
        """
        expire principal
        :param user: <str> username
        :return: <bool> status
        """
        principal = self.admin.getprinc(user)
        if principal:
            principal.expire = datetime.datetime(2010, 12, 31, 23, 0)
            principal.commit()
            return True
        return False

    def activate_principal(self, user):
        """
        activate principal when principal expired
        :param user: <str> username
        :return: <bool> status
        """
        principal = self.admin.getprinc(user)
        if principal:
            principal.expire = datetime.datetime(2037, 12, 31, 23, 0)
            principal.commit()
            return True
        return False

    def get_principal_info(self, user):
        """
        get principal information
        :param user: <str> username
        :return: <dict> principal information
        """
        principal = self.admin.getprinc(user)

        if principal:
            return {
                'principal': principal.principal,
                'name': principal.name,
                'mod_date': principal.mod_date,
                'last_pwd_change': principal.last_pwd_change,
                'last_success': principal.last_success,
                'last_failure': principal.last_failure,
                'maxlife': self._str_timedelta(principal.maxlife),
                'maxrenewlife': self._str_timedelta(principal.maxrenewlife),
                'kvno': principal.kvno,
                'expire': principal.expire
            }
        else:
            return None

    def export_principal(self, user, path):
        return self._kadmin_shell('xst -k {0} {1}'.format(path, user))

    def delete_principal(self, user):
        return self._kadmin_shell('delprinc {0}'.format(user))

    def _str_timedelta(self, obj):
        if isinstance(obj, datetime.timedelta):
            return int(obj.total_seconds())
        else:
            return str(obj)

    def __del__(self):
        if os.path.isfile('/etc/krb5.conf'):
            run_shell('sudo rm /etc/krb5.conf'.format(self.config))
