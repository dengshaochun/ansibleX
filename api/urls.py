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
router.register(r'books', views.BookViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'userProfiles', views.UserProfileViewSet)
router.register(r'userBooks', views.UserBookViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls))
]
