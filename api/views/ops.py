#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/7 14:28
# @Author  : Dengsc
# @Site    : 
# @File    : ansible.py
# @Software: PyCharm


import logging
from rest_framework import viewsets
from api.serializers import *

logger = logging.getLogger(__name__)


class InventoryViewSet(viewsets.ModelViewSet):

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer


class InventoryGroupViewSet(viewsets.ModelViewSet):
    queryset = InventoryGroup.objects.all()
    serializer_class = InventoryGroupSerializer


class AvailableModuleViewSet(viewsets.ModelViewSet):

    queryset = AvailableModule.objects.all()
    serializer_class = AvailableModuleSerializer


class AnsibleScriptViewSet(viewsets.ModelViewSet):

    queryset = AnsibleScript.objects.all()
    serializer_class = AnsibleScriptSerializer


class AnsiblePlayBookViewSet(viewsets.ModelViewSet):

    queryset = AnsiblePlayBook.objects.all()
    serializer_class = AnsiblePlayBookSerializer


class AnsibleConfigViewSet(viewsets.ModelViewSet):

    queryset = AnsibleConfig.objects.all()
    serializer_class = AnsibleConfigSerializer


class AnsibleLockViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsibleLock.objects.all()
    serializer_class = AnsibleLockSerializer


class AnsibleScriptTaskViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsibleScriptTask.objects.all()
    serializer_class = AnsibleScriptTaskSerializer


class AnsiblePlayBookTaskViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsiblePlayBookTask.objects.all()
    serializer_class = AnsiblePlayBookTaskSerializer


class AnsibleScriptTaskScheduleViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsibleScriptTaskSchedule.objects.all()
    serializer_class = AnsibleScriptTaskScheduleSerializer


class AnsiblePlayBookTaskScheduleViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsiblePlayBookTaskSchedule.objects.all()
    serializer_class = AnsiblePlayBookTaskScheduleSerializer


class AnsibleScriptTaskLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsibleScriptTaskLog.objects.all()
    serializer_class = AnsibleScriptTaskLogSerializer


class AnsiblePlayBookTaskLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsiblePlayBookTaskLog.objects.all()
    serializer_class = AnsiblePlayBookTaskLogSerializer


class GitProjectViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = GitProject.objects.all()
    serializer_class = GitProjectSerializer


class ProjectTaskViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ProjectTask.objects.all()
    serializer_class = ProjectTaskSerializer


class ProjectTaskLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ProjectTaskLog.objects.all()
    serializer_class = ProjectTaskLogSerializer


class AlertViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Alert.objects.all()
    serializer_class = AlertSerializer


class AlertLevelViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AlertLevel.objects.all()
    serializer_class = AlertLevelSerializer


class AlertGroupViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AlertGroup.objects.all()
    serializer_class = AlertGroupSerializer


class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AlertLog.objects.all()
    serializer_class = AlertLogSerializer
