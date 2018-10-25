from django.db import models

import uuid
import yaml
import pickle
from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from assets.models import Asset, SystemUser
from utils.encrypt import PrpCrypt


# Create your models here.

ANSIBLE_EXEC_TYPES = (
    ('script', 'script'),
    ('playbook', 'playbook'),
    ('other', 'other')
)


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

    inventory_id = models.UUIDField(_('inventory id'), default=uuid.uuid4(),
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
                    host_var['host_vars'][h.host.ip] = h.get_json_extra_vars()

        inventory_dict['_meta'] = host_var

        return inventory_dict


class InventoryGroup(models.Model):

    name = models.CharField(_('inventory group name'),
                            max_length=80)
    hosts = models.ManyToManyField('InventoryHost',
                                   verbose_name=_('inventory hosts'))
    extra_vars = models.TextField(_('extra vars'),
                                  validators=[validate_dict_format, ],
                                  blank=True, null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return self.name


class InventoryHost(models.Model):

    host = models.ForeignKey(Asset, verbose_name=_('inventory host'),
                             on_delete=models.CASCADE)
    extra_vars = models.TextField(_('extra vars'),
                                  validators=[validate_dict_format, ],
                                  blank=True, null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return '{0}'.format(self.host.ip)

    class Meta:
        unique_together = (('host', 'extra_vars'),)


class AnsibleConfig(models.Model):

    config_id = models.UUIDField(default=uuid.uuid4,
                                 verbose_name=_('module uuid'), unique=True)
    config_name = models.CharField(_('ansible config name'),
                                   max_length=80, unique=True)
    forks = models.IntegerField(_('ansible forks'),
                                default=5)
    timeout = models.IntegerField(_('ansible timeout(s)'),
                                  default=60)
    pattern = models.CharField(_('ansible pattern'),
                               max_length=80, default='all')
    remote_user = models.CharField(_('ansible remote user'),
                                   max_length=80, default='root')
    module_path = models.CharField(_('ansible module path'),
                                   max_length=20,
                                   blank=True, null=True)
    connection_type = models.CharField(_('ansible module path'),
                                       max_length=20, default='smart')
    become = models.BooleanField(_('ansible become'), default=False)
    become_method = models.CharField(_('ansible become method'),
                                     max_length=20,
                                     default='sudo')
    become_user = models.CharField(_('ansible become user'),
                                   max_length=100,
                                   blank=True, null=True)
    ssh_pass = models.CharField(_('ansible ssh password'),
                                max_length=80, blank=True, null=True)
    become_pass = models.CharField(_('ansible become password'),
                                   max_length=80, blank=True, null=True)
    check = models.BooleanField(_('ansible check'), default=False)
    private_key_file = models.FileField(upload_to='private_keys',
                                        verbose_name=_('private key file path'),
                                        blank=True, null=True)
    verbosity = models.IntegerField(_('ansible verbosity'),
                                    default=0)
    diff = models.BooleanField(_('ansible diff'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              null=True)
    public = models.BooleanField(_('public config status'), default=False)

    def __str__(self):
        return self.config_name

    def get_real_passwords(self):
        passwords = {}
        if self.ssh_pass:
            passwords['ssh_pass'] = PrpCrypt().decrypt(self.ssh_pass)
        if self.become_pass:
            passwords['become_pass'] = PrpCrypt().decrypt(
                self.become_pass)
        return passwords

    def get_json_config(self):
        config = {
            'forks': self.forks,
            'connection': self.connection_type,
            'timeout': self.timeout,
            'module_path': self.module_path,
            'become': self.become,
            'become_method': self.become_method,
            'become_user': self.become_user,
            'check': self.check,
            'remote_user': self.remote_user,
            'passwords': self.get_real_passwords(),
            'verbosity': self.verbosity,
            'private_key_file': self.private_key_file,
            'diff': self.diff,
            'pattern': self.pattern
        }

        return config

    def save(self, *args, **kwargs):
        if self.ssh_pass:
            self.ssh_pass = PrpCrypt().encrypt(self.ssh_pass)

        if self.become_pass:
            self.become_pass = PrpCrypt().encrypt(self.become_pass)

        super(AnsibleConfig, self).save(*args, **kwargs)


class AvailableModule(models.Model):

    name = models.CharField(max_length=50,
                            verbose_name=_('module name'), unique=True)
    desc = models.CharField(max_length=200,
                            verbose_name=_('module desc'))
    active = models.BooleanField(_('active status'), default=True)
    public = models.BooleanField(_('public status'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              null=True)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    def __str__(self):
        return self.name


class AnsibleScript(models.Model):

    script_id = models.UUIDField(default=uuid.uuid4,
                                 verbose_name=_('module uuid'), unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('user module name'))
    ansible_module = models.ForeignKey('AvailableModule',
                                       verbose_name=_('ansible module'),
                                       on_delete=models.CASCADE,
                                       null=True)
    module_args = models.TextField(verbose_name=_('script args'),
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


class AnsiblePlayBook(models.Model):

    playbook_id = models.UUIDField(default=uuid.uuid4,
                                   verbose_name=_('playbook uuid'), unique=True)
    name = models.CharField(max_length=50,
                            verbose_name=_('playbook name'))
    desc = models.CharField(max_length=200,
                            verbose_name=_('playbook description'),
                            blank=True, null=True)
    extra_vars = models.TextField(verbose_name=_('playbook vars'),
                                  blank=True, null=True,
                                  validators=[validate_dict_format, ])
    file_path = models.FileField(upload_to='playbooks',
                                 verbose_name=_('playbook file path'))
    concurrent = models.BooleanField(_('concurrent'), default=False)
    public = models.BooleanField(_('public status'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              on_delete=models.SET_NULL,
                              null=True)

    def get_json_extra_vars(self):
        return dict(yaml.safe_load(self.extra_vars)) if self.extra_vars else {}

    def __str__(self):
        return self.name


class AnsibleExecLog(models.Model):

    log_id = models.UUIDField(default=uuid.uuid4,
                              verbose_name=_('log uuid'), unique=True)
    ansible_type = models.CharField(_('ansible type'), max_length=20,
                                    choices=ANSIBLE_EXEC_TYPES)
    object_id = models.CharField(verbose_name=_('execute object id'),
                                 max_length=100,
                                 null=True)
    inventory_id = models.CharField(verbose_name=_('execute inventory id'),
                                    max_length=100,
                                    null=True)
    config_id = models.CharField(verbose_name=_('config id'),
                                 max_length=100,
                                 null=True)
    user_input = models.TextField(_('user input args'), blank=True, null=True)
    succeed = models.BooleanField(_('result status'), default=True)
    full_log = models.TextField(_('full log'), blank=True, null=True)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    def get_full_log(self):
        if self.full_log:
            return pickle.loads(self.full_log)
        else:
            return ''

    def save(self, *args, **kwargs):
        if self.full_log:
            self.full_log = pickle.dumps(self.full_log)
        super(AnsibleExecLog, self).save(*args, **kwargs)

    def __str__(self):
        return self.log_id


class AnsibleRunning(models.Model):

    ansible_type = models.CharField(_('ansible type'), max_length=20,
                                    choices=ANSIBLE_EXEC_TYPES)
    running_id = models.UUIDField(_('running id'))
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    class Meta:
        unique_together = (('ansible_type', 'running_id'),)

    def __str__(self):
        return '{0}:{1}'.format(self.ansible_type, self.running_id)
