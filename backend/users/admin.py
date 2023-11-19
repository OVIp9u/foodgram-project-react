from django.contrib import admin

from .models import User, Subscribe

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username',
        'first_name', 'last_name',
    )
    search_fields = (
        'email', 'username',
        'first_name', 'last_name',
        )
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'


admin.site.register(Subscribe)