from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the Custom User model."""
    model = CustomUser
    list_display = ('username', 'email', 'is_online', 'last_seen', 'is_staff')
    list_filter = ('is_online', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Chat Status', {'fields': ('is_online', 'last_seen')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email',)}),
    )
