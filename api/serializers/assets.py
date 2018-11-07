#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 17:46
# @Author  : Dengsc
# @Site    : 
# @File    : serializers.py
# @Software: PyCharm


from rest_framework import serializers
from assets.models import Asset, AssetGroup, SystemUser


class AssetSerializer(serializers.ModelSerializer):
    system_user = serializers.SlugRelatedField(
        slug_field='name',
        queryset=SystemUser.objects.all())
    asset_group = serializers.SlugRelatedField(
        slug_field='name',
        queryset=AssetGroup.objects.all(),
        many=True)

    class Meta:
        model = Asset
        fields = '__all__'


class AssetGroupSerializer(serializers.ModelSerializer):
    asset_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AssetGroup
        fields = '__all__'


class SystemUserSerializer(serializers.ModelSerializer):
    user_password = serializers.CharField(required=True,
                                          style={'input_type': 'password'},
                                          write_only=True)
    asset_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = SystemUser
        exclude = ('password', )
