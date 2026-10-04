from django.contrib import admin  # type: ignore
from django.contrib.auth.admin import UserAdmin  # type: ignore
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Role & Phone', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Role & Phone', {'fields': ('role', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
