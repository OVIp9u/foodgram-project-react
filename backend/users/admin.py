from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username',
        'first_name', 'last_name',
        'password',
    )
    search_fields = (
        'id', 'email', 'username',
        'first_name', 'last_name',
        )
    list_filter = (
        'id', 'email', 'username',
        'first_name', 'last_name',
    )
    empty_value_display = '-пусто-'


admin.site.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user','author',
    )

    search_fields = (
        'user',
        'author',
    )
