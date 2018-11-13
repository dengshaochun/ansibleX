from django.contrib import admin

# Register your models here.

from accounts.models import Profile, ProfileGroup


class ProfileAdmin(admin.ModelAdmin):

    model = Profile
    search_fields = ('user_id', 'username')
    list_display = ('user_id', 'username', 'chinese_name', 'active')


class ProfileGroupAdmin(admin.ModelAdmin):

    model = ProfileGroup
    search_fields = ('name', )
    list_display = ('name', 'desc', 'create_time')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileGroup, ProfileGroupAdmin)
