from rest_framework.permissions import BasePermission

# Custom Permission Classes for Users App
#
# This module defines custom permission classes that extend Django REST Framework's
# permission system to implement role-based access control.


class IsAdmin(BasePermission):
    """
    Custom permission class that allows access only to admin users.

    This permission class checks if the requesting user:
    1. Is authenticated (logged in)
    2. Has the 'admin' role in their user profile

    Usage:
        Apply this permission to views/viewsets that should only be accessible
        to users with admin privileges.

        Example:
            @permission_classes([IsAdmin])
            def admin_only_view(request):
                # Only admin users can access this view
                pass

    Returns:
        bool: True if user is authenticated and has admin role, False otherwise
    """

    def has_permission(self, request, view):
        """
        Check if the user has admin permissions.

        Args:
            request: The HTTP request object containing user information
            view: The view being accessed (not used in this implementation)

        Returns:
            bool: True if user is authenticated admin, False otherwise
        """
        return bool(
            request.user  # User object exists
            and request.user.is_authenticated  # User is logged in
            and request.user.role == "admin"  # User has admin role
        )
