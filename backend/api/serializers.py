from django.db import models, transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import fields, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscribe, User


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

   
class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиенты в рецепте."""
    id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = '__all__'
        model = RecipeIngredient


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and bool(Subscribe.objects.filter(user=user, author=obj))
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор чтение рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = fields.SerializerMethodField(read_only=True)
    is_in_shopping_cart = fields.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            quantity=models.F('recipeingredient__quantity')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.favorites.filter(recipe=obj).exists()
            and user.is_authenticated
        )
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.shopping_cart(recipe=obj).exists()
            and user.is_authenticated
        )

    class Meta:
        fields = '__all__'
        model = Recipe


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор подписки."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                code=status.HTTP_400_BAD_REQUEST,
                detail='Вы уже подписаны!',
            )
        if user == author:
            raise ValidationError(
                code=status.HTTP_400_BAD_REQUEST,
                detail='Нельзя подписаться на себя!',
            )
        return data

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('username', 'email')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи рецепта."""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()


    def validate_ingredients(self, value):
        
        if not value:
            raise ValidationError({
                'ingredients': 'Для блюда нужен хотя бы один ингредиент!'
            })
        
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Этот ингредиент уже был!'
                })
            if int(item['quantity']) <= 0:
                raise ValidationError({
                    'quantity': 'Количество должно быть больше 0!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Такой тег уже есть!'
                })
            tags_list.append(tag)
        return value

    class Meta:
        fields = '__all__'
        model = Recipe


    @transaction.atomic
    def create_ingredients_quantity(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                quantity=ingredient['quantity']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        self.create_ingredients_quantity(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_quantity(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор карточки рецепта."""
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe