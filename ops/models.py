from django.db import models

import uuid
import yaml
import pickle
from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from assets.models import Asset, SystemUser


# Create your models here.


def validate_dict_format(value):
    """
    validate string is python dict format
    :param value: <str>
    :return: None
    """
    try:
        dict(yaml.safe_load(value))
    except Exception:
        raise ValidationError(
            _('%(value)s is not an python dict decode string.'),
            params={'value': value},
        )


class Inventory(models.Model):
    inventory_id = models.UUIDField(_('module id'), default=uuid.uuid4(),
                                    unique=True)
    name = models.CharField(_('inventory name'),
                            max_length=80)
    groups = models.ManyToManyField('InventoryGroup',
                                    verbose_name=_('inventory groups'))
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              null=True)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    last_modified_time = models.DateTimeField(_('last modified time'),
                                              auto_now=True)

    def __str__(self):
        return self.name

    def get_json_inventory(self):
        inventory_dict = {}
        host_var = {'host_vars': {}}

        for g in self.groups.all():
            inventory_dict.setdefault(g.name, {})
            inventory_dict[g.name]['hosts'] = []
            if g.extra_vars:
                inventory_dict[g.name]['vars'] = g.get_json_extra_vars()
            for h in g.hosts.all():
                if h.host.active:
                    inventory_dict[g.name]['hosts'].append(h.host.ip)

                    extra_var = h.get_json_extra_vars()
                    if h.auth:
                        auth_var = {
                            'ansible_ssh_user': h.auth.name,
                            'ansible_ssh_password': h.auth.get_real_password()
                        }
                    else:
                        auth_var = {}

                    auth_var.update(extra_var)
                    host_var['host_vars'][h.host.ip] = auth_var

        inventory_dict['_meta'] = host_var

        return inventory_dict


class InventoryGroup(models.Model):
    name = models.CharField(_('inventory group name'),
                            max_length=80)
    hosts = models.ManyToManyField('InventoryGroupHost',
                                   verbose_name=_('inventory hosts'))
    extra_vars = models.TextField(_('extra vars'),
                                  validators=[validate_dict_format, ],
                                  blank=True, null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return self.name


class InventoryGroupHost(models.Model):
    host = models.ForeignKey(Asset, verbose_name=_('inventory host'),
                             on_delete=models.CASCADE)
    auth = models.ForeignKey(SystemUser,
                             verbose_name=_('ssh user and password'),
                             on_delete=models.SET_NULL,
                             null=True)
    extra_vars = models.TextField(_('extra vars'),
                                  validators=[validate_dict_format, ],
                                  blank=True, null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return '{0}'.format(self.host.ip)

    class Meta:
        unique_together = (('host', 'auth', 'extra_vars'),)


class AnsibleModule(models.Model):
    module_id = models.UUIDField(_('module id'), default=uuid.uuid4(),
                                 unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('module name'), unique=True)
    desc = models.CharField(max_length=200,
                            verbose_name=_('module description'),
                            blank=True, null=True)

    def __str__(self):
        return self.name


class AnsiblePlayBook(models.Model):
    playbook_id = models.UUIDField(_('playbook id'), default=uuid.uuid4(),
                                   unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('playbook name'))
    desc = models.CharField(max_length=200,
                            verbose_name=_('playbook description'),
                            blank=True, null=True)
    extra_vars = models.TextField(verbose_name=_('playbook vars'),
                                  blank=True, null=True,
                                  validators=[validate_dict_format, ])
    file = models.FileField(upload_to='playbook',
                            verbose_name=_('playbook file path'))
    concurrent = models.BooleanField(_('concurrent'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return self.name


class AnsibleScript(models.Model):
    script_id = models.UUIDField(_('script id'), default=uuid.uuid4(),
                                 unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('script name'))
    ansible_module = models.ForeignKey(AnsibleModule,
                                       verbose_name=_('ansible module'),
                                       on_delete=models.CASCADE,
                                       null=True)
    args = models.TextField(verbose_name=_('script args'),
                            blank=True, null=True)
    extra_vars = models.TextField(verbose_name=_('script extra vars'),
                                  blank=True, null=True,
                                  validators=[validate_dict_format, ])
    desc = models.CharField(max_length=200,
                            verbose_name=_('script description'),
                            blank=True, null=True)
    concurrent = models.BooleanField(_('concurrent'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return self.name


class AnsiblePlayBookLog(models.Model):
    log_id = models.UUIDField(default=uuid.uuid4,
                              verbose_name=_('log uuid'), unique=True)
    playbook = models.ForeignKey(AnsiblePlayBook, verbose_name=_('playbook'),
                                 on_delete=models.SET_NULL,
                                 null=True)
    inventory = models.ForeignKey(Inventory, verbose_name=_('inventory'),
                                  on_delete=models.SET_NULL,
                                  null=True)
    succeed = models.BooleanField(_('result status'), default=True)
    full_log = models.TextField(_('full log'), blank=True, null=True)
    simple_log = models.FileField(upload_to='logs/ansible/%Y%m%d',
                                  verbose_name=_('simple log path'))

    def get_full_log(self):
        return pickle.loads(self.full_log)

    def save(self, *args, **kwargs):
        self.full_log = pickle.dumps(self.full_log)
        super(AnsiblePlayBookLog, self).save(*args, **kwargs)

    def __str__(self):
        return self.log_id


class AnsibleScriptLog(models.Model):
    log_id = models.UUIDField(default=uuid.uuid4,
                              verbose_name=_('log uuid'), unique=True)
    script = models.ForeignKey(AnsibleScript, verbose_name=_('playbook'),
                               on_delete=models.SET_NULL,
                               null=True)
    inventory = models.ForeignKey(Inventory, verbose_name=_('inventory'),
                                  on_delete=models.SET_NULL,
                                  null=True)
    succeed = models.BooleanField(_('result status'), default=True)
    full_log = models.TextField(_('full log'), blank=True, null=True)
    simple_log = models.FileField(upload_to='logs/ansible/%Y%m%d',
                                  verbose_name=_('simple log path'))

    def get_full_log(self):
        return pickle.loads(self.full_log)

    def save(self, *args, **kwargs):
        self.full_log = pickle.dumps(self.full_log)
        super(AnsibleScriptLog, self).save(*args, **kwargs)

    def __str__(self):
        return self.log_id


class AnsibleRunning(models.Model):
    LOCK_TYPES = (
        ('command', 'command'),
        ('script', 'script'),
        ('playbook', 'playbook')
    )

    ansible_type = models.CharField(_('ansible type'), max_length=20,
                                    choices=LOCK_TYPES)
    running_id = models.UUIDField(_('running id'))
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    class Meta:
        unique_together = (('ansible_type', 'running_id'),)

    def __str__(self):
        return '{0}:{1}'.format(self.ansible_type, self.running_id)
