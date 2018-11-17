#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 15:55
# @Author  : Dengsc
# @Site    : 
# @File    : common.py
# @Software: PyCharm

from celery import shared_task
from ops.models.kdc import Principal
from utils.kadmin_api import Kadmin


def get_admin(instance):
    return Kadmin(instance.kdc.admin_principal,
                  instance.kdc.admin_password,
                  instance.kdc.admin_keytab,
                  instance.kdc.abs_config_path,
                  instance.kdc.realms)


@shared_task
def run_add_principal_task(principal_id):
    instance = Principal.objects.get(pk=principal_id)
    admin = get_admin(instance)
    result = admin.add_principal(instance.user.username)
    del admin
    return result


@shared_task
def run_expire_principal_task(principal_id):
    instance = Principal.objects.get(pk=principal_id)
    admin = get_admin(instance)
    result = admin.expire_principal(instance.user.username)
    del admin
    return result


@shared_task
def run_delete_principal_task(principal_id):
    instance = Principal.objects.get(pk=principal_id)
    admin = get_admin(instance)
    result = admin.expire_principal(instance.user.username)
    del admin
    return result
