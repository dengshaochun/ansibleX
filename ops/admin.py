from django.contrib import admin
from django.contrib import messages

# Register your models here.

from ops.models import (Inventory, AnsiblePlayBook, AvailableModule,
                        AnsibleScript, InventoryGroup, AnsibleConfig,
                        AnsibleExecLog, AnsibleRunning, GitProject,
                        ProjectActionLog)


class InventoryAdmin(admin.ModelAdmin):

    model = Inventory
    search_fields = ('name', 'inventory_id', 'owner')
    list_display = ('inventory_id', 'name', 'owner')
    filter_horizontal = ('groups',)
    readonly_fields = ('create_time', )


class InventoryGroupAdmin(admin.ModelAdmin):

    model = InventoryGroup
    search_fields = ('name', )
    list_display = ('name', )
    filter_horizontal = ('assets', 'asset_groups', 'asset_tags')


class AnsiblePlayBookAdmin(admin.ModelAdmin):

    model = AnsiblePlayBook
    search_fields = ('playbook_id', 'name')
    list_display = ('playbook_id', 'name', 'concurrent', 'owner')
    readonly_fields = ('playbook_id',)


class AvailableModuleAdmin(admin.ModelAdmin):

    model = AvailableModule
    search_fields = ('name', 'active', 'public', 'owner')
    list_display = ('name', 'active', 'public', 'owner')


class AnsibleScriptAdmin(admin.ModelAdmin):

    model = AnsibleScript
    search_fields = ('script_id', 'name')
    list_display = ('script_id', 'name', 'concurrent', 'owner')
    readonly_fields = ('script_id',)


class AnsibleConfigAdmin(admin.ModelAdmin):

    model = AnsibleConfig
    search_fields = ('config_id', 'config_name', 'public', 'owner')
    list_display = ('config_id', 'config_name', 'public', 'owner')
    readonly_fields = ('config_id', )


class AnsibleExecLogAdmin(admin.ModelAdmin):

    model = AnsibleExecLog
    search_fields = ('log_id', 'ansible_type', 'object_id', 'succeed')
    list_display = ('log_id', 'ansible_type',
                    'object_id', 'succeed', 'create_time')
    readonly_fields = ('log_id', 'ansible_type', 'object_id', 'succeed',
                       'create_time', 'full_log', 'user_input', 'config_id',
                       'inventory_id')


class AnsibleRunningAdmin(admin.ModelAdmin):

    model = AnsibleRunning
    search_fields = ('ansible_type', 'running_id')
    list_display = ('ansible_type', 'running_id', 'create_time')
    readonly_fields = ('ansible_type', 'running_id', 'create_time')


class GitProjectAdmin(admin.ModelAdmin):

    model = GitProject
    actions = ['clone_git_project', 'pull_git_project', 'remove_local_dir',
               'find_playbooks']
    search_fields = ('project_id', 'name')
    list_display = ('project_id', 'name', 'current_version', 'owner',
                    'last_update_time')
    readonly_fields = ('current_version', 'last_update_time', 'project_id',
                       'local_dir')

    def clone_git_project(self, request, queryset):
        for q in queryset:
            result = q.do_project_action(action='clone')
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def pull_git_project(self, request, queryset):
        for q in queryset:
            result = q.do_project_action(action='pull')
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def remove_local_dir(self, request, queryset):
        for q in queryset:
            result = q.do_clean_local_path()
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def find_playbooks(self, request, queryset):
        for q in queryset:
            result = q.find_playbooks(owner=request.user)
            if result.get('succeed'):
                messages.add_message(request, messages.INFO, result.get('msg'))
            else:
                messages.add_message(request, messages.ERROR, result.get('msg'))

    def save_model(self, request, obj, form, change):
        obj.token = obj.auth_token
        super().save_model(request, obj, form, change)

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


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryGroup, InventoryGroupAdmin)
admin.site.register(AnsiblePlayBook, AnsiblePlayBookAdmin)
admin.site.register(AvailableModule, AvailableModuleAdmin)
admin.site.register(AnsibleScript, AnsibleScriptAdmin)
admin.site.register(AnsibleConfig, AnsibleConfigAdmin)
admin.site.register(AnsibleExecLog, AnsibleExecLogAdmin)
admin.site.register(AnsibleRunning, AnsibleRunningAdmin)
admin.site.register(GitProject, GitProjectAdmin)
admin.site.register(ProjectActionLog, ProjectActionLogAdmin)
