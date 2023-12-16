from django.db import models
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, fields, serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribe, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed',
        )
        read_only_fields = ('id',)
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.subscribing.filter(user=user).exists()
        )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор подписки."""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeMinSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscribeUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/удаления подписки."""

    class Meta:
        model = Subscribe
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на этого автора.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                {'error': 'Нельзя подписаться на себя.'}
            )
        return super().validate(data)

    def to_representation(self, instance):
        """Вывод данных сериализатором рецепта."""
        return SubscribeSerializer(
            instance.author, context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега"""
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента"""
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецепта."""
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = fields.SerializerMethodField(read_only=True)
    is_in_shopping_cart = fields.SerializerMethodField(read_only=True)

    class Meta:
        fields = fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart',
            'name', 'image', 'text',
            'cooking_time',
        )
        model = Recipe

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=models.F('recipeingredient__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is not None:
            return (
                request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists()
            )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is not None:
            return (
                request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists()
            )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(use_url=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = '__all__'

    def validate(self, attrs):
        if 'tags' not in attrs.keys():
            raise exceptions.ValidationError(
                {'tags': 'Отсутствует поле "Теги"!'},
            )
        if 'ingredients' not in attrs.keys():
            raise exceptions.ValidationError(
                {'tags': 'Отсутствует поле "Ингредиенты"!'},
            )
        return super().validate(attrs)

    def validate_image(self, value):
        if not value:
            raise exceptions.ValidationError(
                {'image': 'Нужна фотография рецепта'}
            )
        return value

    def validate_cooking_time(self, value):
        if value > 32767:
            raise exceptions.ValidationError(
                {'cooking_time': 'Время приготовления больше 32767!'}
            )
        if value < 1:
            raise exceptions.ValidationError(
                {'cooking_time': 'Время приготовления не может быть меньше 1!'}
            )
        return value

    def validate_tags(self, value):
        if len(value) < 1 or not value:
            raise exceptions.ValidationError(
                {'tags': 'Нужно выбрать хотя бы один тег!'}
            )
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise exceptions.ValidationError({
                    'tags': 'Такой тег уже есть!'
                })
            tags_list.append(tag)
        return value

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise exceptions.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for ingredient in ingredients:
            try:
                current_ingredient = Ingredient.objects.get(
                    id=ingredient['id']
                )
            except Exception:
                raise exceptions.ValidationError({
                    'ingredients': 'Такого ингредиента нет в базе!'
                })
            if current_ingredient in ingredients_list:
                raise exceptions.ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            if int(ingredient['amount']) < 1:
                raise exceptions.ValidationError({
                    'amount': 'Количество ингредиента не может быть меньше 1!'
                })
            ingredients_list.append(current_ingredient)
        return ingredients

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    def create_ingredients_amounts(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance, context=context).data


class RecipeMinSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта мини."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class AbstractSerializer(serializers.ModelSerializer):
    """Абстрактный сериализатор корзина/избранное."""

    class Meta:
        abstract = True

    def validate(self, data):
        """Валидация на повторное добавление."""
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(
            user=user, recipe=recipe
        ).exists():
            raise exceptions.ValidationError(
                {'error': 'Этот рецепт уже добавлен.'}
            )
        return data

    def to_representation(self, instance):
        """Вывод данных сериализатором рецепта."""
        return RecipeMinSerializer(instance.recipe).data


class FavoriteRecipeSerializer(AbstractSerializer):
    """Сериализатор добавления в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        return super().validate(data)


class ShoppingCartSerializer(AbstractSerializer):
    """Сериализатор добавления в корзину."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
