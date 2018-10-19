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
                              on_delete=models.SET_NULL)
    create_time = models.DateTimeField(_('create time'), auto_created=True)
    last_modified_time = models.DateTimeField(_('last modified time'),
                                              auto_now=True)

    def __str__(self):
        return self.name

    def get_json_inventory(self):
        inventory_dict = {}
        for g in self.groups.all():
            inventory_dict[g.name]['hosts'] = []
            inventory_dict[g.name]['vars'] = dict(g.ext_vars)
            for h in g.hosts.all():
                if h.host.active:
                    inventory_dict[g.name]['hosts'].append(h.ip)
                    inventory_dict['_meta']['hostvars'][h.host.ip] = dict(
                        h.ext_vars)
        return inventory_dict


class InventoryGroup(models.Model):

    name = models.CharField(_('inventory group name'),
                            max_length=80)
    hosts = models.ManyToManyField('InventoryGroupHost',
                                   verbose_name=_('inventory hosts'))
    ext_vars = models.TextField(_('extra vars'),
                                validators=[validate_dict_format, ],
                                blank=True, null=True)

    def __str__(self):
        return self.name


class InventoryGroupHost(models.Model):

    host = models.ForeignKey(Asset, verbose_name=_('inventory host'),
                             on_delete=models.CASCADE)
    auth = models.ForeignKey(SystemUser,
                             verbose_name=_('ssh user and password'),
                             on_delete=models.SET_NULL)
    ext_vars = models.TextField(_('extra vars'),
                                validators=[validate_dict_format, ],
                                blank=True, null=True)

    def __str__(self):
        return '{0}'.format(self.host.ip)


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


class AnsiblePlaybook(models.Model):

    playbook_id = models.UUIDField(_('playbook id'), default=uuid.uuid4(),
                                   unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('playbook name'))
    desc = models.CharField(max_length=200,
                            verbose_name=_('playbook description'),
                            blank=True, null=True)
    vars = models.TextField(verbose_name=_('playbook vars'),
                            blank=True, null=True)
    file = models.FileField(upload_to='playbook',
                            verbose_name=_('playbook file path'))
    concurrent = models.BooleanField(_('concurrent'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class AnsibleScript(models.Model):

    script_id = models.UUIDField(_('script id'), default=uuid.uuid4(),
                                 unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('script name'))
    ansible_module = models.ForeignKey(AnsibleModule,
                                       verbose_name=_('ansible module'),
                                       on_delete=models.CASCADE)
    vars = models.TextField(verbose_name=_('script vars'),
                            blank=True, null=True)
    desc = models.CharField(max_length=200,
                            verbose_name=_('script description'),
                            blank=True, null=True)
    concurrent = models.BooleanField(_('concurrent'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class AnsiblePlayBookLog(models.Model):

    log_id = models.UUIDField(default=uuid.uuid4,
                              verbose_name=_('log uuid'), unique=True)
    playbook = models.ForeignKey(AnsiblePlaybook, verbose_name=_('playbook'),
                                 on_delete=models.SET_NULL,
                                 related_name='log_playbook')
    inventory = models.ForeignKey(Inventory, verbose_name=_('inventory'),
                                  on_delete=models.SET_NULL,
                                  related_name='log_inventory')
    succeed = models.BooleanField(_('result status'), default=True)
    _json_log = models.TextField(_('full json log'), blank=True, null=True)
    simple_log = models.FileField(upload_to='logs/ansible/%Y%m%d',
                                  verbose_name=_('simple log path'))

    @property
    def json_log(self):
        return pickle.loads(self._json_log)

    @json_log.setter
    def json_log(self, value):
        self._json_log = pickle.dumps(value)

    def __str__(self):
        return self.log_id


class AnsibleScriptLog(models.Model):

    log_id = models.UUIDField(default=uuid.uuid4,
                              verbose_name=_('log uuid'), unique=True)
    script = models.ForeignKey(AnsibleScript, verbose_name=_('playbook'),
                               on_delete=models.SET_NULL,
                               related_name='log_script')
    inventory = models.ForeignKey(Inventory, verbose_name=_('inventory'),
                                  on_delete=models.SET_NULL,
                                  related_name='log_inventory')
    succeed = models.BooleanField(_('result status'), default=True)
    _json_log = models.TextField(_('full json log'), blank=True, null=True)
    simple_log = models.FileField(upload_to='logs/ansible/%Y%m%d',
                                  verbose_name=_('simple log path'))

    @property
    def json_log(self):
        return pickle.loads(self._json_log)

    @json_log.setter
    def json_log(self, value):
        self._json_log = pickle.dumps(value)

    def __str__(self):
        return self.log_id


class AnsibleLock(models.Model):

    LOCK_TYPES = (
        ('command', 'command'),
        ('script', 'script'),
        ('playbook', 'playbook')
    )

    lock_type = models.CharField(_('lock type'), max_length=20,
                                 choices=LOCK_TYPES)
    lock_id = models.UUIDField(_('lock id'))
    create_time = models.DateTimeField(_('create time'), auto_created=True)

    class Meta:
        unique_together = (('lock_type', 'lock_id'),)

    def __str__(self):
        return '{0}:{1}'.format(self.lock_type, self.lock_id)
