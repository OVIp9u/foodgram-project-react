from django.urls import include, path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

from .views import CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

# app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet)


urlpatterns = [

    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
