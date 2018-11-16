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


class KDCServer(models.Model):

    name = models.CharField(_('kdc name'), max_length=100, unique=True)
    realms = models.CharField(_('kdc name'), max_length=50)
    hosts = models.ManyToManyField(Asset, verbose_name=_('kdc hosts'))
    admin_server = models.ForeignKey(Asset, verbose_name=_('admin server host'),
                                     on_delete=models.SET_NULL, null=True)
    config_file = models.FileField(upload_to='config/kdc/',
                                   verbose_name=_('kdc config file'),
                                   blank=True, null=True)
    admin_principal = models.CharField(_('principal name'), max_length=50)
    admin_password = models.CharField(_('principal password'), max_length=50,
                                      null=True, blank=True)
    admin_keytab = models.FileField(upload_to='config/kdc/',
                                    verbose_name=_('kdc config file'),
                                    blank=True, null=True)

    def validate_unique(self, *args, **kwargs):
        super(KDCServer, self).validate_unique(*args, **kwargs)
        if not self.admin_password and not self.admin_keytab:
            raise ValidationError({
                'interval': [
                    'One of admin_password, admin_keytab must be set.'
                ]
            })

    def __str__(self):
        return '{0} {1}'.format(self.realms, self.name)


class Principal(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user of principal'),
                             on_delete=models.CASCADE)
    kdc = models.ForeignKey('KDCServer', verbose_name=_('kdc server'),
                            on_delete=models.CASCADE)
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)

    @property
    def principal_info(self):
        from utils.kadmin_api import Kadmin
        abs_config_path = os.path.join(settings.MEDIA_ROOT,
                                       self.kdc.config_file.url)
        admin = Kadmin(self.kdc.admin_principal, self.kdc.admin_password,
                       self.kdc.admin_keytab, abs_config_path,
                       self.kdc.realms)
        principal = admin.get_principal_info(self.user.username)
        del admin
        return principal

    def __str__(self):
        return '{0} {1}'.format(self.kdc.name, self.user.username)
