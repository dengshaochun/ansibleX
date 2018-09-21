from django.shortcuts import render

# Create your views here.

import logging
from rest_framework import viewsets
from app.models import Book, Category, UserBook, UserProfile, Tag
from api.serializers import (BookSerializer, CategorySerializer, TagSerializer,
                             UserProfileSerializer, UserBookSerializer)

logger = logging.getLogger(__name__)


class BookViewSet(viewsets.ModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserProfileViewSet(viewsets.ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserBookViewSet(viewsets.ModelViewSet):
    queryset = UserBook.objects.all()
    serializer_class = UserBookSerializer
