from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


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


class InlineRecipeIngredient(admin.StackedInline):
    """Вывод ингредиентов на страницу рецепта."""
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов в админке."""
    list_display = [
        'author',
        'name',
        'text',
        'cooking_time',
        'add_to_favorite'
    ]
    list_filter = [
        'name',
        'author'
    ]
    empty_value_display = ' пусто '
    inlines = (InlineRecipeIngredient, )

    @admin.display(
        description='Количество добавлений в избранное'
    )
    def add_to_favorite(self, obj):
        return obj.favorites.count()
