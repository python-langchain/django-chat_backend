from django.contrib import admin
from .models import User

# Django Admin Configuration for Users App
#
# This module configures the Django admin interface for the User model,
# providing an intuitive interface for administrators to manage users.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the User model.

    Provides a comprehensive admin interface with:
    - List view showing key user information
    - Search functionality across email, full name, and nickname
    - Filtering and sorting capabilities
    """

    # Fields to display in the admin list view
    list_display = (
        "id",  # User ID for reference
        "email",  # Primary identifier
        "full_name",  # User's complete name
        "nickname",  # Display name
        "role",  # User role (user/admin)
        "is_active",  # Account status
        "is_staff",  # Staff privileges
    )

    # Fields that can be searched in the admin interface
    # Enables quick user lookup by email, name, or nickname
    search_fields = ("email", "full_name", "nickname")
