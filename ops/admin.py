from django.contrib import admin
from django.contrib import messages

# Register your models here.

from ops.models import (Inventory, AnsiblePlayBook, AvailableModule,
                        AnsibleScript, InventoryGroup, AnsibleConfig,
                        AnsibleExecLog, AnsibleLock, GitProject,
                        ProjectActionLog, Alert, AlertLevel, AlertGroup,
                        AlertLog)
from ops.tasks import run_project_command


class InventoryAdmin(admin.ModelAdmin):

    model = Inventory
    search_fields = ('name', 'inventory_id')
    list_display = ('inventory_id', 'name', 'owner')
    filter_horizontal = ('groups',)
    readonly_fields = ('create_time', 'owner')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class InventoryGroupAdmin(admin.ModelAdmin):

    model = InventoryGroup
    search_fields = ('name', )
    list_display = ('name', )
    filter_horizontal = ('assets', 'asset_groups', 'asset_tags')


class AnsiblePlayBookAdmin(admin.ModelAdmin):

    model = AnsiblePlayBook
    search_fields = ('playbook_id', 'name')
    list_display = ('playbook_id', 'name', 'concurrent', 'owner')
    readonly_fields = ('playbook_id', 'owner')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AvailableModuleAdmin(admin.ModelAdmin):

    model = AvailableModule
    search_fields = ('name', 'active', 'public')
    list_display = ('name', 'active', 'public', 'owner')
    readonly_fields = ('owner', )

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AnsibleScriptAdmin(admin.ModelAdmin):

    model = AnsibleScript
    search_fields = ('script_id', 'name')
    list_display = ('script_id', 'name', 'concurrent', 'owner')
    readonly_fields = ('script_id', 'owner')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AnsibleConfigAdmin(admin.ModelAdmin):

    model = AnsibleConfig
    search_fields = ('config_id', 'config_name', 'public')
    list_display = ('config_id', 'config_name', 'public', 'owner')
    readonly_fields = ('config_id', 'owner')

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = AnsibleConfig.objects.get(pk=obj.pk)
            if old_obj.ssh_pass != obj.ssh_pass:
                obj.ssh_password = obj.ssh_pass
            if old_obj.become_pass != obj.become_pass:
                obj.become_password = obj.become_pass
        else:
            obj.ssh_password = obj.ssh_pass
            obj.become_password = obj.become_pass

        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AnsibleExecLogAdmin(admin.ModelAdmin):

    model = AnsibleExecLog
    search_fields = ('log_id', 'ansible_type', 'object_id', 'succeed')
    list_display = ('log_id', 'ansible_type',
                    'object_id', 'succeed', 'create_time')
    readonly_fields = ('log_id', 'ansible_type', 'object_id', 'succeed',
                       'create_time', 'full_log', 'user_input', 'config_id',
                       'inventory_id')


class AnsibleLockAdmin(admin.ModelAdmin):

    model = AnsibleLock
    search_fields = ('ansible_type', 'lock_object_id')
    list_display = ('ansible_type', 'lock_object_id', 'create_time')
    readonly_fields = ('ansible_type', 'lock_object_id', 'create_time')


class GitProjectAdmin(admin.ModelAdmin):

    model = GitProject
    actions = ['clone_git_project', 'pull_git_project', 'remove_local_dir',
               'find_playbooks']
    search_fields = ('project_id', 'name')
    list_display = ('project_id', 'name', 'current_version', 'owner',
                    'last_update_time')
    readonly_fields = ('current_version', 'last_update_time', 'project_id',
                       'local_dir', 'owner')

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = GitProject.objects.get(pk=obj.pk)
            if old_obj.auth_token != obj.auth_token:
                obj.token = obj.auth_token
        else:
            obj.token = obj.auth_token

        obj.owner = request.user
        super().save_model(request, obj, form, change)

    def clone_git_project(self, request, queryset):
        for q in queryset:
            result = run_project_command(q.project_id, 'clone', request.user.pk)
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def pull_git_project(self, request, queryset):
        for q in queryset:
            result = run_project_command(q.project_id, 'pull', request.user.pk)
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def remove_local_dir(self, request, queryset):
        for q in queryset:
            result = run_project_command(q.project_id, 'clean', request.user.pk)
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def find_playbooks(self, request, queryset):
        for q in queryset:
            result = run_project_command(q.project_id, 'find', request.user.pk)
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    clone_git_project.short_description = 'clone project'
    pull_git_project.short_description = 'pull project'
    remove_local_dir.short_description = 'remove local dir'
    find_playbooks.short_description = 'find playbooks'


class ProjectActionLogAdmin(admin.ModelAdmin):

    model = ProjectActionLog
    search_fields = ('log_id', 'action_type', 'action_status')
    list_display = ('log_id', 'action_type', 'action_status', 'action_time')
    readonly_fields = ('log_id', 'action_type', 'action_status', 'action_time',
                       'project', 'action_log')


class AlertAdmin(admin.ModelAdmin):

    model = Alert
    search_fields = ('alert_id', )
    list_display = ('alert_id', 'level', 'owner')
    filter_horizontal = ('groups', )
    readonly_fields = ('alert_id', 'owner')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AlertGroupAdmin(admin.ModelAdmin):

    model = AlertGroup
    search_fields = ('name', )
    list_display = ('name', 'owner', 'last_modified_time')
    filter_horizontal = ('users', )
    readonly_fields = ('owner', 'last_modified_time')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AlertLevelAdmin(admin.ModelAdmin):

    model = AlertLevel
    search_fields = ('name',)
    list_display = ('name', 'desc')


class AlertLogAdmin(admin.ModelAdmin):

    model = AlertLog
    search_fields = ('log_id', 'status')
    list_display = ('log_id', 'status')
    readonly_fields = ('log_id', 'alert', 'content', 'status')


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryGroup, InventoryGroupAdmin)
admin.site.register(AnsiblePlayBook, AnsiblePlayBookAdmin)
admin.site.register(AvailableModule, AvailableModuleAdmin)
admin.site.register(AnsibleScript, AnsibleScriptAdmin)
admin.site.register(AnsibleConfig, AnsibleConfigAdmin)
admin.site.register(AnsibleExecLog, AnsibleExecLogAdmin)
admin.site.register(AnsibleLock, AnsibleLockAdmin)
admin.site.register(GitProject, GitProjectAdmin)
admin.site.register(ProjectActionLog, ProjectActionLogAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertGroup, AlertGroupAdmin)
admin.site.register(AlertLevel, AlertLevelAdmin)
admin.site.register(AlertLog, AlertLogAdmin)
