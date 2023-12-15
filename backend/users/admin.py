from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение пользователей в админке."""
    list_display = (
        'id', 'email', 'username',
        'first_name', 'last_name',
        'password', 'recipes',
        'subscribers'
    )
    search_fields = (
        'username', 'first_name', 'last_name',
    )
    list_filter = (
        'email', 'username',
    )
    empty_value_display = '-пусто-'

    @admin.display(
        description='Количество рецептов'
    )
    def recipes(self, obj):
        return obj.recipes.count()

    @admin.display(
        description='Количество подписчиков'
    )
    def subscribers(self, obj):
        return obj.subscriber.count()


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
