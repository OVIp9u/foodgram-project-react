from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeGetSerializer, ShoppingCartSerializer,
                             SubscribeSerializer, SubscribeUpdateSerializer,
                             TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscribe, User


class CustomUserViewSet(views.UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator

    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписка."""
        subscriptions = User.objects.filter(
            subscribing__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Добавление/удаление подписки."""
        get_object_or_404(User, id=id)
        data = {
            'author': id,
            'user': request.user.id
        }

        serializer = SubscribeUpdateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        get_object_or_404(User, id=id)
        user = request.user
        obj = Subscribe.objects.filter(
            user=user, author=id
        )
        if obj.exists():
            obj.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Подписки не существует',
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('name',)

    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    permission_classes = [
        IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly
    ]
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('name',)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        """Выбор сериализатора для рецептов."""
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавление в корзину."""
        return self.add_to(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        """Удаление из корзины."""
        return self.delete_from(ShoppingCart, request, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавление в избранное."""
        return self.add_to(FavoriteRecipeSerializer, request, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        """Удаление из избранного."""
        return self.delete_from(Favorite, request, pk)

    @staticmethod
    def add_to(serializer, request, pk):
        """Добавление в модель."""
        data = {
            'user': request.user.pk,
            'recipe': pk,
        }
        serializer_instance = serializer(data=data,
                                         context={'request': request})
        serializer_instance.is_valid(raise_exception=True)
        serializer_instance.save()
        return Response(serializer_instance.data,
                        status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_from(model, request, pk):
        """Удаление из покупок и избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Этой записи не существует'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание файла с корзиной."""
        user = request.user

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(cart_amount=Sum('amount'))
        shopping_cart = ['Список покупок:']

        for ingredient in ingredients:
            shopping_cart.append(
                f'{ingredient["ingredient__name"]} '
                f'{ingredient["cart_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )

        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            f'{user.username}_shopping_cart.txt'
        )
        return response
