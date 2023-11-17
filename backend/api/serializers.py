import datetime as dt
import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Tag

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега"""
    class Meta:
        model = Tag
        fields = '__all__'