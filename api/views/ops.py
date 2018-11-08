#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/7 14:28
# @Author  : Dengsc
# @Site    : 
# @File    : ansible.py
# @Software: PyCharm


import logging
from rest_framework import viewsets
from ops.models import (Inventory, InventoryGroup, AvailableModule,
                        AnsibleScript, AnsiblePlayBook, AnsibleConfig,
                        AnsibleLock, AnsibleExecLog)
from api.serializers import (InventorySerializer, InventoryGroupSerializer,
                             AvailableModuleSerializer, AnsibleScriptSerializer,
                             AnsiblePlayBookSerializer, AnsibleConfigSerializer,
                             AnsibleLockSerializer, AnsibleExecLogSerializer)

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


class AnsibleExecLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AnsibleExecLog.objects.all()
    serializer_class = AnsibleExecLogSerializer
