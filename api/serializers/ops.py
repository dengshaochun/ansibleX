#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/7 14:30
# @Author  : Dengsc
# @Site    : 
# @File    : ops.py
# @Software: PyCharm

from rest_framework import serializers
from ops.models import (InventoryGroup, Inventory, AnsiblePlayBook,
                        AvailableModule, AnsibleLock, AnsibleExecLog,
                        AnsibleConfig, AnsibleScript)


class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('inventory_id', 'owner',
                            'create_time', 'last_modified_time')


class InventoryGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = InventoryGroup
        fields = '__all__'


class AvailableModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvailableModule
        fields = '__all__'
        read_only_fields = ('owner', 'create_time')


class AnsiblePlayBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsiblePlayBook
        fields = '__all__'
        read_only_fields = ('owner', 'playbook_id')


class AnsibleScriptSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsibleScript
        fields = '__all__'
        read_only_fields = ('owner', 'script_id')


class AnsibleConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsibleConfig
        fields = '__all__'
        read_only_fields = ('owner', 'config_id')


class AnsibleLockSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsibleLock
        fields = '__all__'


class AnsibleExecLogSerializer(serializers.ModelSerializer):
    completed_log = serializers.CharField(read_only=True)

    class Meta:
        model = AnsibleExecLog
        exclude = ('full_log', )
