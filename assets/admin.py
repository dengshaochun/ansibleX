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


class AssetGroupAdmin(admin.ModelAdmin):

    model = AssetGroup
    search_fields = ('name', 'owner')
    list_display = ('name', 'owner', 'desc')


class SystemUserAdmin(admin.ModelAdmin):

    model = SystemUser
    search_fields = ('name', )
    list_display = ('name', 'owner', 'create_time')


admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetTag, AssetTagAdmin)
admin.site.register(AssetGroup, AssetGroupAdmin)
admin.site.register(SystemUser, SystemUserAdmin)
