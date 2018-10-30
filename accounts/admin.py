from django.contrib import admin

# Register your models here.

from accounts.models import UserProfile, UserGroup


class UserProfileAdmin(admin.ModelAdmin):

    model = UserProfile
    search_fields = ('user_id', 'username')
    list_display = ('user_id', 'username', 'chinese_name', 'active')


class UserGroupAdmin(admin.ModelAdmin):

    model = UserGroup
    search_fields = ('name', )
    list_display = ('name', 'desc', 'create_time')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
