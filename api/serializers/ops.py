#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/7 14:30
# @Author  : Dengsc
# @Site    : 
# @File    : ops.py
# @Software: PyCharm

from rest_framework import serializers
from ops.models import (InventoryGroup, Inventory, AnsiblePlayBook,
                        AvailableModule, AnsibleLock, AnsibleScriptTask,
                        AnsiblePlayBookTask, AnsibleConfig, AnsibleScript,
                        GitProject, ProjectTask, AnsibleScriptTaskLog,
                        AnsiblePlayBookTaskLog, ProjectTaskLog, Alert,
                        AlertLevel, AlertGroup, AnsiblePlayBookTaskSchedule,
                        AnsibleScriptTaskSchedule, AlertLog)


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


class AnsibleScriptTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsibleScriptTask
        fields = '__all__'


class AnsiblePlayBookTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsiblePlayBookTask
        fields = '__all__'


class GitProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = GitProject
        fields = '__all__'


class ProjectTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTask
        fields = '__all__'


class AnsibleScriptTaskScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsibleScriptTaskSchedule
        fields = '__all__'


class AnsiblePlayBookTaskScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsiblePlayBookTaskSchedule
        fields = '__all__'


class AnsiblePlayBookTaskLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsiblePlayBookTaskLog
        fields = '__all__'


class AnsibleScriptTaskLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsibleScriptTaskLog
        fields = '__all__'


class ProjectTaskLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTaskLog
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = '__all__'


class AlertLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertLevel
        fields = '__all__'


class AlertGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertGroup
        fields = '__all__'


class AlertLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertLog
        fields = '__all__'
