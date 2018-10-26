from django.contrib import admin

# Register your models here.

from ops.models import (Inventory, AnsiblePlayBook, AvailableModule,
                        AnsibleScript, InventoryGroup, InventoryHost,
                        AnsibleConfig, AnsibleExecLog, AnsibleRunning)


class InventoryAdmin(admin.ModelAdmin):

    list_display = ('inventory_id', 'name', 'owner')
    filter_horizontal = ('groups',)
    readonly_fields = ('create_time', )


class InventoryGroupAdmin(admin.ModelAdmin):

    list_display = ('name', )
    filter_horizontal = ('hosts',)


class InventoryHostAdmin(admin.ModelAdmin):

    list_display = ('host', )


class AnsiblePlayBookAdmin(admin.ModelAdmin):

    list_display = ('playbook_id', 'name', 'concurrent', 'owner')


class AvailableModuleAdmin(admin.ModelAdmin):

    list_display = ('name', 'active', 'public', 'owner')


class AnsibleScriptAdmin(admin.ModelAdmin):

    list_display = ('script_id', 'name', 'concurrent', 'owner')


class AnsibleConfigAdmin(admin.ModelAdmin):
    list_display = ('config_id', 'config_name', 'public', 'owner')


class AnsibleExecLogAdmin(admin.ModelAdmin):

    list_display = ('log_id', 'ansible_type',
                    'object_id', 'succeed', 'create_time')
    readonly_fields = ('log_id', 'ansible_type', 'object_id', 'succeed',
                       'create_time', 'full_log', 'user_input', 'config_id',
                       'inventory_id'
                       )


class AnsibleRunningAdmin(admin.ModelAdmin):

    list_display = ('ansible_type', 'running_id', 'create_time')
    readonly_fields = ('ansible_type', 'running_id', 'create_time')


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryGroup, InventoryGroupAdmin)
admin.site.register(InventoryHost, InventoryHostAdmin)
admin.site.register(AnsiblePlayBook, AnsiblePlayBookAdmin)
admin.site.register(AvailableModule, AvailableModuleAdmin)
admin.site.register(AnsibleScript, AnsibleScriptAdmin)
admin.site.register(AnsibleConfig, AnsibleConfigAdmin)
admin.site.register(AnsibleExecLog, AnsibleExecLogAdmin)
admin.site.register(AnsibleRunning, AnsibleRunningAdmin)
