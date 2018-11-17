from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from utils.encrypt import PrpCrypt
from utils.validators import convert_json_to_dict, validate_dict_format

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
                                    related_name='asset_group_assets',
                                    blank=True,
                                    null=True)
    asset_tags = models.ManyToManyField('AssetTag',
                                        verbose_name=_('asset tags'))
    active = models.BooleanField(_('active status'), default=True)
    extra_vars = models.TextField(_('extra vars'),
                                  validators=[validate_dict_format, ],
                                  blank=True, null=True)
    system_user = models.ForeignKey('SystemUser',
                                    verbose_name=_('system user'),
                                    on_delete=models.SET_NULL,
                                    related_name='system_user_assets',
                                    blank=True,
                                    null=True)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))

    def get_json_extra_vars(self):
        return convert_json_to_dict(self.extra_vars) if self.extra_vars else {}

    def get_json_principal_vars(self):
        principals_1 = [x.user.username
                        for x in self.asset_profile_assets.all()
                        if x.user.active and x.user.principal_info]
        principals_2 = [x.user.username
                        for x in self.asset_group.asset_group_profile_assets.all()
                        if x.user.active and x.user.principal_info]
        principals_3 = []
        for tag in self.asset_tags.all():
            principals_3 += [x.user.username
                             for x in tag.profileasset_set.all()
                             if x.user.active and x.user.principal_info]

        return {
            'host_principals': set(principals_1 + principals_2 + principals_3)
        }

    def get_json_tag_vars(self):
        return {
            'host_tags': [x.name for x in self.asset_tags.all()]
        }

    def get_json_group_vars(self):
        return {
            'host_group': self.asset_group.name
        }

    def get_json_meta_vars(self):
        meta_vars = self.get_json_extra_vars()
        meta_vars.update(self.get_json_principal_vars())
        meta_vars.update(self.get_json_tag_vars())
        meta_vars.update(self.get_json_group_vars())
        return meta_vars

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

    @property
    def user_password(self):
        return self.password

    @user_password.setter
    def user_password(self, value):
        self.password = PrpCrypt().encrypt(value)

    def __str__(self):
        return self.name
