from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение тегов в админке."""
    list_display = [
        'name',
        'color',
        'slug'
    ]
    empty_value_display = ' пусто '


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов в админке."""
    list_display = [
        'name',
        'measurement_unit',
    ]
    list_filter = [
        'name'
    ]
    empty_value_display = ' пусто '


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов в админке."""
    list_display = [
        'author',
        'name',
        'text',
        'cooking_time',
    ]
    list_filter = [
        'name',
        'author'
    ]
    empty_value_display = ' пусто '
