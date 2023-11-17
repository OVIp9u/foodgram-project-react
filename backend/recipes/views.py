from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
#from rest_framework_simplejwt.tokens import AccessToken
#from django_filters import rest_framework as filters_df
from .models import Recipe
from .serializers import RecipeSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer