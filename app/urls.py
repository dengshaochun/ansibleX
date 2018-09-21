#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 15:28
# @Author  : Dengsc
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:room_name>/', views.room, name='room'),
]
