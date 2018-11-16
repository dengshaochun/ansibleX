#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:25
# @Author  : Dengsc
# @Site    : 
# @File    : kadmin_api.py
# @Software: PyCharm


import os
import kadmin
import datetime
from utils.shell_api import run_shell


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
        else:
            self.admin = kadmin.init_with_keytab(
                admin_principal, admin_keytab)

    def _setup_config(self):
        """
        copy krb5.conf /etc/ directory
        :return: <bool> status
        """

        # Todo make sure only one instance
        if os.path.isfile(self.config):
            result = run_shell('sudo cp {0} /etc/'.format(self.config))
            return result.get('succeed')
        return False

    def add_principal(self, user):
        """
        add principal
        :param user: <str> username
        :return: <dict> principal information
        """
        self.admin.addprinc(user)
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
                'maxlife': principal.maxlife,
                'maxrenewlife': principal.maxrenewlife,
                'kvno': principal.kvno,
                'expire': principal.expire
            }
        else:
            return None

    def __del__(self):
        pass
