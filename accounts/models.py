from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from assets.models import Asset, AssetTag, AssetGroup

# Create your models here.


class Profile(models.Model):
    ACCOUNT_CHOICES = (
        (0, 'private'),
        (1, 'public'),
        (-1, 'unknown')
    )

    user_id = models.IntegerField(_('portal id'),
                                  blank=True,
                                  null=True,
                                  help_text=_('company portal id'))
    username = models.CharField(_('username'),
                                max_length=100,
                                unique=True)
    phone = models.CharField(_('phone number'), max_length=20,
                             blank=True, null=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    chinese_name = models.CharField(_('chinese name'),
                                    max_length=100,
                                    blank=True,
                                    null=True)
    active = models.BooleanField(_('active'),
                                 default=True)
    department_name = models.CharField(_('department name'),
                                       max_length=300,
                                       blank=True,
                                       null=True)
    account_type = models.IntegerField(_('account type'),
                                       choices=ACCOUNT_CHOICES,
                                       default=0)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))
    last_modified_time = models.DateTimeField(_('last modified time'),
                                              auto_now=True)
    sys_account = models.OneToOneField(User, verbose_name=_('django user'),
                                       on_delete=models.SET_NULL, null=True,
                                       blank=True)

    @property
    def principal_info(self):
        return self.sys_account.principal.principal_info

    def __str__(self):
        return self.username


class ProfileGroup(models.Model):

    name = models.CharField(_('profile group name'),
                            max_length=100,
                            unique=True)
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('create time'))
    desc = models.CharField(_('description'),
                            max_length=100,
                            blank=True,
                            null=True)

    def __str__(self):
        return self.name


class ProfileAsset(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user'),
                             on_delete=models.CASCADE,
                             related_name='user_profile_assets')
    asset = models.ForeignKey(Asset, verbose_name=_('profile assets'),
                              on_delete=models.SET_NULL,
                              related_name='asset_profile_assets',
                              null=True)
    asset_group = models.ForeignKey(
        AssetGroup, verbose_name=_('profile asset groups'),
        on_delete=models.SET_NULL, related_name='asset_group_profile_assets',
        null=True)
    asset_tag = models.ForeignKey(AssetTag,
                                  verbose_name=_('profile asset tags'),
                                  on_delete=models.SET_NULL,
                                  related_name='asset_tag_profile_assets',
                                  null=True)
    created_time = models.DateTimeField(_('create time'), auto_now_add=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL, null=True,
                              related_name='owner_profile_assets')

    class Meta:
        unique_together = (('user', 'asset'),
                           ('user', 'asset_group'),
                           ('user', 'asset_tag'))

    @property
    def assets(self):
        assets_1 = [self.asset, ] if self.asset else []
        assets_2 = [x for x in
                    self.asset_group.asset_group_assets.all() if x.active]
        assets_3 = [x for x in self.asset_tag.asset_set.all() if x.active]

        return set(assets_1 + assets_2 + assets_3)

    def __str__(self):
        return self.pk
