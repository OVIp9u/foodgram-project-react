from django.contrib import admin
from django.contrib.admin import display

from .models import Ingredient, Recipe, Tag, RecipeIngredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'color',
        'slug'
    ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'measurement_unit',
    ]
    list_filter = [
        'name'
    ]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
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


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = [
        'recipe',
        'ingredient',
        'quantity'
    ]
