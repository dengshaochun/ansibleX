from django.contrib import admin
from django.contrib import messages

# Register your models here.

from ops.models import (Inventory, AnsiblePlayBook, AvailableModule,
                        AnsibleScript, InventoryGroup, AnsibleConfig,
                        AnsibleScriptTask, AnsiblePlayBookTask,
                        AnsibleLock, GitProject,
                        ProjectTask, Alert, AlertLevel, AlertGroup,
                        AlertLog, DingTalk, AnsibleScriptTaskSchedule,
                        AnsiblePlayBookTaskSchedule, AnsiblePlayBookTaskLog,
                        AnsibleScriptTaskLog, ProjectTaskLog)


class InventoryAdmin(admin.ModelAdmin):

    model = Inventory
    search_fields = ('name', 'inventory_id')
    list_display = ('inventory_id', 'name', 'owner')
    filter_horizontal = ('groups',)
    readonly_fields = ('inventory_id', 'create_time', 'owner')

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
    search_fields = ('instance_id', 'name')
    list_display = ('instance_id', 'name', 'concurrent', 'owner')
    readonly_fields = ('instance_id', 'owner')

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
    search_fields = ('instance_id', 'name')
    list_display = ('instance_id', 'name', 'concurrent', 'owner')
    readonly_fields = ('instance_id', 'owner')

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


class AnsibleScriptTaskAdmin(admin.ModelAdmin):

    model = AnsibleScriptTask
    search_fields = ('task_id', )
    list_display = ('task_id', 'owner', 'created_time')
    readonly_fields = ('task_id', 'created_time', 'owner')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AnsiblePlayBookTaskAdmin(admin.ModelAdmin):
    model = AnsiblePlayBookTask
    search_fields = ('task_id', )
    list_display = ('task_id', 'owner', 'created_time')
    readonly_fields = ('task_id', 'created_time',  'owner')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AnsibleLockAdmin(admin.ModelAdmin):

    model = AnsibleLock
    search_fields = ('lock_object_id', )
    list_display = ('lock_object_id', 'created_time')
    readonly_fields = ('lock_object_id', 'created_time')


class GitProjectAdmin(admin.ModelAdmin):

    model = GitProject
    search_fields = ('project_id', 'name')
    list_display = ('project_id', 'name', 'current_version', 'owner',
                    'last_modified_time')
    readonly_fields = ('current_version', 'last_modified_time', 'project_id',
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


class ProjectTaskAdmin(admin.ModelAdmin):

    model = ProjectTask
    search_fields = ('task_id', 'action_type')
    list_display = ('task_id', 'action_type', 'created_time')
    readonly_fields = ('task_id', 'created_time')


class AlertAdmin(admin.ModelAdmin):

    model = Alert
    search_fields = ('name', )
    list_display = ('name', 'level', 'email', 'ding_talk', 'owner')
    filter_horizontal = ('groups', )
    readonly_fields = ('owner', )

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


class DingTalkAdmin(admin.ModelAdmin):

    model = DingTalk
    search_fields = ('name', 'url', 'msg_type')
    list_display = ('name', 'url', 'msg_type', 'at_all', 'owner')
    readonly_fields = ('owner', )

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AnsibleScriptTaskScheduleAdmin(admin.ModelAdmin):

    model = AnsibleScriptTaskSchedule
    search_fields = ('name', )
    list_display = ('name', 'enabled')


class AnsiblePlayBookTaskScheduleAdmin(admin.ModelAdmin):

    model = AnsiblePlayBookTaskSchedule
    search_fields = ('name', )
    list_display = ('name', 'enabled')


class AnsibleScriptTaskLogAdmin(admin.ModelAdmin):

    model = AnsibleScriptTaskLog
    search_fields = ('log_id', )
    list_display = ('log_id', 'task', 'succeed')
    readonly_fields = ('log_id', 'task', 'succeed', 'task_log')


class AnsiblePlayBookTaskLogAdmin(admin.ModelAdmin):

    model = AnsiblePlayBookTaskLog
    search_fields = ('log_id', )
    list_display = ('log_id', 'task', 'succeed')
    readonly_fields = ('log_id', 'task', 'succeed', 'task_log')


class ProjectTaskLogAdmin(admin.ModelAdmin):

    model = ProjectTaskLog
    search_fields = ('log_id', )
    list_display = ('log_id', 'task', 'succeed')
    readonly_fields = ('log_id', 'task', 'succeed', 'task_log')


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryGroup, InventoryGroupAdmin)
admin.site.register(AnsiblePlayBook, AnsiblePlayBookAdmin)
admin.site.register(AvailableModule, AvailableModuleAdmin)
admin.site.register(AnsibleScript, AnsibleScriptAdmin)
admin.site.register(AnsibleConfig, AnsibleConfigAdmin)
admin.site.register(AnsibleScriptTask, AnsibleScriptTaskAdmin)
admin.site.register(AnsiblePlayBookTask, AnsiblePlayBookTaskAdmin)
admin.site.register(AnsibleLock, AnsibleLockAdmin)
admin.site.register(GitProject, GitProjectAdmin)
admin.site.register(ProjectTask, ProjectTaskAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertGroup, AlertGroupAdmin)
admin.site.register(AlertLevel, AlertLevelAdmin)
admin.site.register(AlertLog, AlertLogAdmin)
admin.site.register(DingTalk, DingTalkAdmin)
admin.site.register(AnsibleScriptTaskSchedule, AnsibleScriptTaskScheduleAdmin)
admin.site.register(AnsiblePlayBookTaskSchedule,
                    AnsiblePlayBookTaskScheduleAdmin)
admin.site.register(AnsiblePlayBookTaskLog, AnsiblePlayBookTaskLogAdmin)
admin.site.register(AnsibleScriptTaskLog, AnsibleScriptTaskLogAdmin)
admin.site.register(ProjectTaskLog, ProjectTaskLogAdmin)
