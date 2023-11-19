from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

# app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
