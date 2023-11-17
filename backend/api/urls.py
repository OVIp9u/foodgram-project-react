from django.urls import include, path
from rest_framework import routers
from .views import TagViewSet  #, IngredientViewSet, RecipeViewSet,

#app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', TagViewSet)
#router.register('recipes', RecipeViewSet)
#router.register('ingredients', IngredientViewSet)



urlpatterns = [
    path('', include(router.urls)),
]
