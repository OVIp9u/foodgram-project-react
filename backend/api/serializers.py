import datetime as dt
import re
from django.db import models
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework import serializers, fields

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега"""
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор тега"""
    class Meta:
        fields = '__all__'
        model = Ingredient
        

class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    # author
    #is_favorited = fields.SerializerMethodField(read_only=True)
    #is_in_shopping_cart = fields.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=models.F('recipeingredient__quantity')
        )
        return ingredients

    '''def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.favorites.filter(recipe=obj).exists()
            and
            user.is_authenticated
        )
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.shopping_cart(recipe=obj).exists()
            and
            user.is_authenticated
        )'''

    class Meta:
        fields = '__all__'
        model = Recipe
   
class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = '__all__'
        model = RecipeIngredient

class RecipeChangeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    # author 
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = '__all__'
        model = Recipe
        

class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
