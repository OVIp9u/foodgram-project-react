from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers
from django.conf import settings
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()


router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )