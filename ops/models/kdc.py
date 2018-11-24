#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 15:57
# @Author  : Dengsc
# @Site    : 
# @File    : kdc.py
# @Software: PyCharm


import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from assets.models import Asset

from utils.encrypt import PrpCrypt


class KDCServer(models.Model):

    name = models.CharField(_('kdc name'), max_length=100, unique=True)
    realms = models.CharField(_('kdc realms'), max_length=50)
    hosts = models.ManyToManyField(Asset, verbose_name=_('kdc hosts'))
    admin_server = models.ForeignKey(Asset, verbose_name=_('admin server host'),
                                     on_delete=models.SET_NULL, null=True,
                                     related_name='admin_server_kdc_servers')
    config_file = models.FileField(upload_to='config/kdc/',
                                   verbose_name=_('kdc config file'),
                                   blank=True, null=True)
    admin_principal = models.CharField(_('admin principal name'), max_length=50)
    admin_password = models.CharField(_('admin principal password'),
                                      max_length=50,
                                      null=True, blank=True)
    admin_keytab = models.FileField(upload_to='config/kdc/',
                                    verbose_name=_('admin keytab file'),
                                    blank=True, null=True)

    def validate_unique(self, *args, **kwargs):
        super(KDCServer, self).validate_unique(*args, **kwargs)
        if not self.admin_password and not self.admin_keytab:
            raise ValidationError({
                'interval': [
                    'One of admin_password, admin_keytab must be set.'
                ]
            })

    @property
    def password(self):
        if self.admin_password:
            return PrpCrypt().decrypt(self.admin_password)
        else:
            return None

    @password.setter
    def password(self, value):
        if value:
            self.admin_password = PrpCrypt().encrypt(value)

    @property
    def abs_config_path(self):
        return os.path.join(settings.BASE_DIR, self.config_file.url[1:])

    def __str__(self):
        return '{0} {1}'.format(self.realms, self.name)


class Principal(models.Model):

    user = models.OneToOneField(User, verbose_name=_('user of principal'),
                                on_delete=models.CASCADE,
                                related_name='user_principal')
    kdc = models.ForeignKey('KDCServer', verbose_name=_('kdc server'),
                            on_delete=models.CASCADE,
                            related_name='kdc_principals')
    active = models.BooleanField(_('active status'), default=True)
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    last_modified_time = models.DateTimeField(_('last modified time'),
                                              auto_now=True)

    @property
    def principal_info(self):
        from utils.kadmin_api import Kadmin
        admin = Kadmin(self.kdc.admin_principal, self.kdc.admin_password,
                       self.kdc.admin_keytab, self.kdc.abs_config_path,
                       self.kdc.realms)
        principal = admin.get_principal_info(self.user.username)
        del admin
        return principal

    def __str__(self):
        return '{0} {1}'.format(self.kdc.name, self.user.username)
