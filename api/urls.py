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
router.register(r'asset_tags', views.AssetTagViewSet)
router.register(r'system_users', views.SystemUserViewSet)
router.register(r'inventories', views.InventoryViewSet)
router.register(r'inventory_groups', views.InventoryGroupViewSet)
router.register(r'available_modules', views.AvailableModuleViewSet)
router.register(r'ansible_configs', views.AnsibleConfigViewSet)
router.register(r'ansible_scripts', views.AnsibleScriptViewSet)
router.register(r'ansible_playbooks', views.AnsiblePlayBookViewSet)
router.register(r'ansible_locks', views.AnsibleLockViewSet)
router.register(r'ansible_script_tasks', views.AnsibleScriptTaskViewSet)
router.register(r'ansible_playbook_tasks', views.AnsiblePlayBookTaskViewSet)
router.register(r'ansible_script_task_schedules',
                views.AnsibleScriptTaskScheduleViewSet)
router.register(r'ansible_playbook_task_schedules',
                views.AnsiblePlayBookTaskScheduleViewSet)
router.register(r'ansible_script_task_logs',
                views.AnsibleScriptTaskLogViewSet)
router.register(r'ansible_playbook_task_logs',
                views.AnsiblePlayBookTaskLogViewSet)
router.register(r'git_projects', views.GitProjectViewSet)
router.register(r'project_tasks', views.ProjectTaskViewSet)
router.register(r'project_task_logs', views.ProjectTaskLogViewSet)
router.register(r'alerts', views.AlertViewSet)
router.register(r'alert_groups', views.AlertGroupViewSet)
router.register(r'alert_levels', views.AlertLevelViewSet)
router.register(r'alert_logs', views.AlertLogViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls))
]
