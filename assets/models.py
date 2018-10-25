from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from utils.encrypt import PrpCrypt

# Create your models here.


class Asset(models.Model):

    ip = models.GenericIPAddressField(_('ip address'), unique=True)
    os = models.CharField(_('operating system'),
                          max_length=50,
                          blank=True,
                          null=True)
    hostname = models.CharField(_('hostname'),
                                max_length=80,
                                blank=True,
                                null=True)
    asset_group = models.ForeignKey('AssetGroup',
                                    verbose_name=_('asset group'),
                                    on_delete=models.SET_NULL,
                                    blank=True,
                                    null=True)
    asset_tag = models.ManyToManyField('AssetTag',
                                       verbose_name=_('asset tags'),
                                       blank=True, null=True)
    active = models.BooleanField(_('active status'), default=True)
    system_user = models.ForeignKey('SystemUser',
                                    verbose_name=_('system user'),
                                    on_delete=models.SET_NULL,
                                    blank=True,
                                    null=True)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))

    def __str__(self):
        return '{0}'.format(self.ip)


class AssetGroup(models.Model):

    name = models.CharField(_('asset group name'),
                            max_length=100,
                            unique=True)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)
    owner = models.ForeignKey(User,
                              verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True)

    def __str__(self):
        return self.name


class AssetTag(models.Model):

    name = models.CharField(_('asset group name'),
                            max_length=100,
                            unique=True)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)
    owner = models.ForeignKey(User,
                              verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True)

    def __str__(self):
        return self.name


class SystemUser(models.Model):

    name = models.CharField(_('ssh user'),
                            max_length=30,
                            unique=True)
    password = models.CharField(_('ssh user password'),
                                max_length=100)
    owner = models.ForeignKey(User,
                              verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))

    def get_real_password(self):
        return PrpCrypt().decrypt(self.password)

    def save(self, *args, **kwargs):
        self.password = PrpCrypt().encrypt(self.password)
        super(SystemUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
