from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение пользователей в админке."""
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


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Отображение подписок в админке."""
    search_fields = (
        'user',
        'author',
    )
    list_display = (
        'id', 'user', 'author',
    )
    empty_value_display = '-пусто-'
