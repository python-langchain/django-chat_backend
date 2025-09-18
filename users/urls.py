from django.urls import path
from . import views

# URL Configuration for Users App
#
# This module defines the URL patterns for user-related endpoints.
# All URLs in this module will be prefixed with the users app URL pattern
# as defined in the main project's urls.py file.

urlpatterns = [
    # User listing and search endpoint
    # GET /users/ - List all users with optional search
    # Query params: ?q=search_term (optional)
    # Permissions: IsAuthenticated (requires login)
    path("", views.list_users, name="users_list"),
    # User registration endpoint
    # POST /users/register/ - Create a new user account
    # Permissions: AllowAny (public endpoint)
    path("register/", views.register, name="register"),
]
