from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username',
        'first_name', 'last_name',
    )
    search_fields = (
        'email', 'username',
        'first_name', 'last_name',
        )
    list_filter = ('id', 'email', 'username', 'first_name', 'last_name',)
    empty_value_display = '-пусто-'


admin.site.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'user',
        'author',
    ]

    search_fields = [
        'user',
        'author',
    ]