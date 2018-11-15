from django.contrib import admin

# Register your models here.

from assets.models import Asset, AssetTag, AssetGroup, SystemUser


class AssetAdmin(admin.ModelAdmin):

    model = Asset
    search_fields = ('ip', 'hostname')
    list_display = ('ip', 'hostname', 'system_user', 'active')
    filter_horizontal = ('asset_tags',)


class AssetTagAdmin(admin.ModelAdmin):

    model = AssetTag
    search_fields = ('name', 'owner')
    list_display = ('name', 'owner', 'desc')
    readonly_fields = ('owner',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class AssetGroupAdmin(admin.ModelAdmin):

    model = AssetGroup
    search_fields = ('name', 'owner')
    list_display = ('name', 'owner', 'desc')
    readonly_fields = ('owner',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


class SystemUserAdmin(admin.ModelAdmin):

    model = SystemUser
    search_fields = ('name', )
    list_display = ('name', 'owner', 'create_time')
    readonly_fields = ('owner',)

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = SystemUser.objects.get(pk=obj.pk)
            if old_obj.password != obj.password:
                obj.user_password = obj.password
        else:
            obj.user_password = obj.password

        obj.owner = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetTag, AssetTagAdmin)
admin.site.register(AssetGroup, AssetGroupAdmin)
admin.site.register(SystemUser, SystemUserAdmin)
