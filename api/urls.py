#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 17:50
# @Author  : Dengsc
# @Site    : 
# @File    : urls.py
# @Software: PyCharm


from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from api import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'assets', views.AssetViewSet)
router.register(r'asset_groups', views.AssetGroupViewSet)
router.register(r'system_users', views.SystemUserViewSet)
router.register(r'inventories', views.InventoryViewSet)
router.register(r'inventory_groups', views.InventoryGroupViewSet)
router.register(r'available_modules', views.AvailableModuleViewSet)
router.register(r'ansible_configs', views.AnsibleConfigViewSet)
router.register(r'ansible_scripts', views.AnsibleScriptViewSet)
router.register(r'ansible_playbooks', views.AnsiblePlayBookViewSet)
router.register(r'ansible_locks', views.AnsibleLockViewSet)
router.register(r'ansible_script_tasks', views.AnsibleScriptTaskViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls))
]
