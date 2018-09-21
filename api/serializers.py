#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/21 17:46
# @Author  : Dengsc
# @Site    : 
# @File    : serializers.py
# @Software: PyCharm


from rest_framework import serializers
from app.models import Book, Category, UserProfile, UserBook, Tag


class BookSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name',
                                            queryset=Category.objects.all())
    tags = serializers.SlugRelatedField(slug_field='name',
                                        queryset=Tag.objects.all(),
                                        many=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'category', 'tags')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    account_type = serializers.ChoiceField(choices=UserProfile.ACCOUNT_CHOICES)
    books = serializers.SlugRelatedField(slug_field='name', many=True,
                                         read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class UserBookSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username',
                                        queryset=UserProfile.objects.all())
    book = serializers.SlugRelatedField(slug_field='name',
                                        queryset=Book.objects.all())

    class Meta:
        model = UserBook
        fields = ('id', 'user', 'book')
