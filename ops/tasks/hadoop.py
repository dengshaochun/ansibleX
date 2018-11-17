#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 15:56
# @Author  : Dengsc
# @Site    : 
# @File    : hadoop.py
# @Software: PyCharm

import logging
import requests
from celery import shared_task

from ops.models.hadoop import CMServer, CDHCluster
from assets.models import Asset, AssetTag, AssetGroup
from utils.encrypt import PrpCrypt

logger = logging.getLogger(__name__)


class CMS(object):

    def __init__(self, cm_name):
        self.cm = CMServer.objects.get(name=cm_name)
        self.auth = (self.cm.auth_user,
                     PrpCrypt().decrypt(self.cm.auth_password))
        self.api_url = '{0}/api/{1}'.format(self.cm.cm_url,
                                            self.cm.api_version)
        self.cm_hosts = None
        self._result = {
            'succeed': True,
            'messages': list()
        }

    def _get_json_response(self, url):
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(e)
            self._result['succeed'] = False
            return None

    def _update_cm_meta(self):
        self._result['cm_meta'] = {}
        self.cm.hosts.update(active=False)
        cm_meta = self._get_json_response('{0}/cm/version'.format(self.api_url))
        self.cm.version = cm_meta.get('version')
        self.cm_hosts = self._get_json_response(
            '{0}/hosts'.format(self.api_url)).get('items', [])
        for cm_host in self.cm_hosts:
            obj = Asset.objects.get_or_create(ip=cm_host.get('ipAddress'))[0]
            asset_group = AssetGroup.objects.get_or_create(
                name='hadoop-node')[0]
            obj.asset_group = asset_group
            obj.active = True
            obj.save()
            if obj not in self.cm.hosts.all():
                self.cm.hosts.add(obj)
        self.cm.save()
        self._result['messages'].append('update cm meta successful!')

    def _update_clusters(self):

        cluster_metas = self._get_json_response(
            '{0}/clusters'.format(self.api_url)).get('items', [])
        for cluster_meta in cluster_metas:
            # update cluster meta
            cluster = CDHCluster.objects.get_or_create(
                cluster_url=cluster_meta.get('clusterUrl'))[0]

            cluster.name = cluster_meta.get('name')
            cluster.display_name = cluster_meta.get('displayName')
            cluster.cm = self.cm
            cluster.version = '{0}|{1}'.format(
                cluster_meta.get('version'),
                cluster_meta.get('fullVersion'))

            tag_name = '{0}-{1}'.format('cluster', cluster.display_name)
            tag_obj = AssetTag.objects.get_or_create(name=tag_name)[0]

            # update cluster hosts
            cluster_hosts = self._get_json_response(
                '{0}/clusters/{1}/hosts'.format(
                    self.api_url, cluster_meta.get('name'))).get('items', [])
            for cluster_host in cluster_hosts:
                host_ips = [x.get('ipAddress')
                            for x in self.cm_hosts
                            if x.get('hostId') == cluster_host.get('hostId')]
                host_ip = host_ips[0]
                obj = Asset.objects.get(ip=host_ip)
                if obj not in cluster.hosts.all():
                    obj.tags.add(tag_obj)
                    cluster.hosts.add(obj)
            cluster.save()
            self._result['messages'].append(
                'update {0} meta successful!'.format(cluster.name))

    def update(self):
        self._update_cm_meta()
        self._update_clusters()
        return self._result


@shared_task
def run_update_cm_server_task(cm_name):
    """
    通过CM url获取集群主机信息
    :param cm_name: <str> cm name
    :return: <dict> result
    """
    return CMS(cm_name=cm_name).update()


@shared_task
def run_update_all_cm_server_task():
    for cm in CMServer.objects.all():
        run_update_cm_server_task(cm_name=cm.name)
