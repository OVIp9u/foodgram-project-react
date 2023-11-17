from rest_framework import filters, mixins, status, viewsets
from .permissions import IsAdminIsAuthorOrReadOnly
from recipes.models import Tag
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .serializers import TagSerializer

class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    pagination_class = None
'''
class IngredientViewSet(viewsets.ModelViewSet):
    ...

class RecipeViewSet(viewsets.ModelViewSet):
    ...

'''