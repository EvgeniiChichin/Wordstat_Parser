from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
    list_filter = ("is_active", "is_staff")
    exclude = ("session_id", "yandexuid")


admin.site.register(CustomUser, CustomUserAdmin)
