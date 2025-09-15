from django.contrib import admin
from .models import User


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "nickname",
        "role",
        "is_active",
        "is_staff",
    )
    search_fields = ("email", "full_name", "nickname")
