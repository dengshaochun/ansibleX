from django.contrib import admin

# Register your models here.

from ops.models import (Inventory, AnsiblePlayBook, AnsibleModule,
                        AnsibleScript, InventoryGroup, InventoryGroupHost)


class InventoryAdmin(admin.ModelAdmin):

    list_display = ('inventory_id', 'name', 'owner')
    filter_horizontal = ('groups',)
    readonly_fields = ('create_time', )


class InventoryGroupAdmin(admin.ModelAdmin):

    list_display = ('name', )
    filter_horizontal = ('hosts',)


class InventoryGroupHostAdmin(admin.ModelAdmin):

    list_display = ('host', )


class AnsiblePlayBookAdmin(admin.ModelAdmin):

    list_display = ('playbook_id', 'name', 'concurrent', 'owner')


class AnsibleModuleAdmin(admin.ModelAdmin):

    list_display = ('module_id', 'name', 'desc')


class AnsibleScriptAdmin(admin.ModelAdmin):

    list_display = ('script_id', 'name', 'concurrent', 'owner')


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryGroup, InventoryGroupAdmin)
admin.site.register(InventoryGroupHost, InventoryGroupHostAdmin)
admin.site.register(AnsiblePlayBook, AnsiblePlayBookAdmin)
admin.site.register(AnsibleModule, AnsibleModuleAdmin)
admin.site.register(AnsibleScript, AnsibleScriptAdmin)
