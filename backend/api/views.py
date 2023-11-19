from rest_framework import filters, mixins, status, viewsets
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from recipes.models import Ingredient, Recipe, Tag
from users.models import User
from djoser import views
from .permissions import IsAdminIsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipePutPatchDeleteSerializer, IngredientRecipeGetSerializer,
                          TagSerializer)
from .serializers import AuthorizedUserSerializer

class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    pagination_class = None

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    pagination_class = None

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    #filter_backends = (DjangoFilterBackend,)
    #filterset_class = RecipeFilter
    #pagination_class = None
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    
    serializer_class = RecipeGetSerializer


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    '''def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePutPatchDeleteSerializer'''

class CustomUserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = AuthorizedUserSerializer
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
