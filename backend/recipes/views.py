from api.pagination import CustomPaginator
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeGetSerializer, RecipeMinSerializer,
                             TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


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
    permission_classes = [IsAuthorOrReadOnly | IsAdminOrReadOnly,]
    filter_backends = (DjangoFilterBackend,)
    search_fields = ("name",)
    filterset_class = RecipeFilter
    ordering = ("-pub_date",)

    def get_serializer_class(self):
        """Выбор сериализатора для рецептов."""
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=[permissions.IsAuthenticated,]
    )
    def favorite(self, request, pk):
        try:
            match request.method:
                case 'POST': return self.add_to(Favorite, request.user, pk)
                case 'DELETE': return self.delete_from(
                    Favorite, request.user, pk
                )
        except:
            return Response(
                {'errors': 'Ошибка добавления в избранное!!'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=[permissions.IsAuthenticated,]
    )
    def shopping_cart(self, request, pk):
        try:
            match request.method:
                case 'POST': return self.add_to(
                    ShoppingCart, request.user, pk
                )
                case 'DELETE': return self.delete_from(
                    ShoppingCart, request.user, pk
                )
        except:
            return Response(
                        {'errors': 'Ошибка добавления в корзину!!'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

    def add_to(self, model, user, id):
        if model.objects.filter(user=user, recipe__id=id).exists():
            raise exceptions.ValidationError(
                {'errors': 'Рецепт уже есть в базе!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinSerializer(recipe)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже удален из базы!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated,]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if user.shopping_cart.exists():
            ingredients = RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(cart_amount=Sum('amount'))
            shopping_cart = ['Список покупок:']
            for ingredient in ingredients:
                shopping_cart.append(
                    f'({ingredient["ingredient__name"]} '
                    f'{ingredient["cart_amount"]} '
                    f'{ingredient["ingredient__measurement_unit"]}'
                )

            file = f'{user.username}_shopping_cart.txt'
            response = HttpResponse(shopping_cart, content_type='text/plain')
            response['Content-Disposition'] = f'{file}'
            return response
        return Response('Корзина пуста', status=status.HTTP_400_BAD_REQUEST)
