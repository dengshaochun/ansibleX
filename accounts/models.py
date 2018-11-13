from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

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
