#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 15:18
# @Author  : Dengsc
# @Site    : 
# @File    : hadoop.py
# @Software: PyCharm

from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from utils.validators import validate_unit
from utils.encrypt import PrpCrypt
from accounts.models import Profile
from assets.models import Asset
from ops.models.kdc import KDCServer


class Acl(models.Model):

    name = models.CharField(_('Acl name'), max_length=50, unique=True)
    permission = models.ForeignKey('AclPermission',
                                   verbose_name=_('permission'),
                                   on_delete=models.CASCADE)
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)

    def __str__(self):
        return self.name


class AclPermission(models.Model):

    name = models.CharField(_('permission name'), max_length=50, unique=True)
    permission = models.CharField(_('acl permission'), max_length=50)

    def __str__(self):
        return self.name


class HiveDataBase(models.Model):

    name = models.CharField(_('database name'), max_length=50)
    path = models.CharField(_('database path'),
                            max_length=50,
                            unique=True)
    space_quota = models.CharField(_('hdfs space quota'),
                                   max_length=50,
                                   default='max',
                                   validators=[validate_unit])
    files_quota = models.BigIntegerField(
        _('files quota'), default=-1,
        help_text=_('set value=-1 mean do not set files quota'))
    acls = models.ManyToManyField('Acl',
                                  verbose_name=_('acls'),
                                  blank=True)
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)
    created_time = models.DateTimeField(_('create time'), auto_now_add=True)
    owners = models.ManyToManyField(Profile,
                                    verbose_name=_('owners'),
                                    blank=True)

    def __str__(self):
        return self.name


class YarnPool(models.Model):

    name = models.CharField(_('Yarn pool name'), max_length=50, unique=True)
    acls = models.ManyToManyField('Acl',
                                  verbose_name=_('acls'),
                                  blank=True)
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)
    leader = models.ManyToManyField(Profile,
                                    verbose_name=_('leader'),
                                    blank=True)

    def __str__(self):
        return self.name


class CMServer(models.Model):

    name = models.CharField(_('cm name'), max_length=50, unique=True)
    cm_url = models.URLField(_('cm url'), max_length=200, unique=True)
    version = models.CharField(_('cm version'),
                               max_length=50,
                               blank=True,
                               null=True)
    api_version = models.CharField(_('api version'),
                                   max_length=20)
    auth_user = models.CharField(_('auth user name'), max_length=50)
    auth_password = models.CharField(_('auth password'), max_length=50)
    hosts = models.ManyToManyField(Asset,
                                   verbose_name=_('hosts'),
                                   blank=True)
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)

    @property
    def password(self):
        return self.auth_password

    @password.setter
    def password(self, value):
        self.auth_password = PrpCrypt().encrypt(value)

    def __str__(self):
        return self.name


class CDHCluster(models.Model):

    name = models.CharField(_('cluster name'), max_length=50)
    cm = models.ForeignKey('CMServer',
                           verbose_name=_('cm server'),
                           on_delete=models.CASCADE,
                           related_name='cm_cdh_clusters')
    kdc = models.ForeignKey(KDCServer, verbose_name=_('kdc server'),
                            on_delete=models.SET_NULL, null=True,
                            related_name='kdc_cdh_clusters')
    cluster_url = models.URLField(_('cluster url'),
                                  max_length=200, unique=True)
    display_name = models.CharField(_('display name'),
                                    max_length=100)
    hosts = models.ManyToManyField(Asset,
                                   verbose_name=_('hosts'),
                                   blank=True)
    version = models.CharField(_('cluster version'),
                               max_length=50,
                               blank=True,
                               null=True)
    last_modified_time = models.DateTimeField(_('last modified time'),
                                              auto_now=True)

    def __str__(self):
        return self.display_name


class HadoopClient(models.Model):

    host = models.ForeignKey(Asset, verbose_name=_('host'),
                             on_delete=models.CASCADE)
    cluster = models.ForeignKey('CDHCluster', verbose_name=_('CDH cluster'),
                                on_delete=models.CASCADE)
    created_time = models.DateTimeField(_('create time'), auto_now_add=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '{0} {1}'.format(self.cluster.display_name, self.host.ip)
