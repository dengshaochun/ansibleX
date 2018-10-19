from django.shortcuts import render

# Create your views here.

import logging
from rest_framework import viewsets
from assets.models import Asset, AssetGroup, SystemUser
from api.serializers import (AssetGroupSerializer, AssetSerializer,
                             SystemUserSerializer)

logger = logging.getLogger(__name__)


class AssetViewSet(viewsets.ModelViewSet):

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class AssetGroupViewSet(viewsets.ModelViewSet):

    queryset = AssetGroup.objects.all()
    serializer_class = AssetGroupSerializer


class SystemUserViewSet(viewsets.ModelViewSet):

    queryset = SystemUser.objects.all()
    serializer_class = SystemUserSerializer
