from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "name"]
    fieldsets = (
        (None, {"fields": ["email", "name", "password"]}),
        (_("Permissions"), {"fields": ["is_staff", "is_active", "is_superuser"]}),
        (_("Special Dates"), {"fields": ["last_login"]}),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": [
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ]
            },
        ),
    )

    readonly_fields = ["last_login"]


# Register your models here.
admin.site.register(User, UserAdmin)
