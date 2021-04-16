from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': (
                    'username', 'email', 'password1', 'password2', 'is_staff',
                ),
            }
        ),
    )
    list_display = ('username', 'email', 'date_joined', 'is_staff')


admin.site.register(CustomUser, CustomUserAdmin)
