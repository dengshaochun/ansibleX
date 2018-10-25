from django.contrib import admin

# Register your models here.

from assets.models import Asset, AssetTag, AssetGroup, SystemUser


class AssetAdmin(admin.ModelAdmin):

    list_display = ('ip', 'hostname', 'system_user', 'active')
    filter_horizontal = ('asset_tag',)


class AssetTagAdmin(admin.ModelAdmin):

    list_display = ('name', 'owner', 'desc')


class AssetGroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'owner', 'desc')


class SystemUserAdmin(admin.ModelAdmin):

    list_display = ('name', 'owner', 'create_time')


admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetTag, AssetTagAdmin)
admin.site.register(AssetGroup, AssetGroupAdmin)
admin.site.register(SystemUser, SystemUserAdmin)
