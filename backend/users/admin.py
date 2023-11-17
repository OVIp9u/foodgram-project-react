from django.contrib import admin
from django.contrib.admin import display

from .models import (Tag)



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'color',
        'slug'
    ]