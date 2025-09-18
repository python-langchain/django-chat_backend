from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, PublicUserSerializer

# User Management Views
# This module contains API views for user registration and user listing functionality

# Get the custom User model
User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user account.

    This endpoint allows anyone to create a new user account.
    The password is validated and securely hashed before storage.

    Method: POST
    Permissions: AllowAny (public endpoint)

    Request Body:
        - email (str): User's email address (required, unique)
        - password (str): Password (required, min 6 characters)
        - full_name (str): User's full name (required)
        - nickname (str): Display name (optional)
        - other_info (dict): Additional user information (optional)

    Returns:
        201: User created successfully with public user data
        400: Validation errors (email already exists, invalid data, etc.)
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        # Return only public information for security
        return Response(
            PublicUserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    List and search users.

    This endpoint allows authenticated users to view a list of all users
    with optional search functionality.

    Method: GET
    Permissions: IsAuthenticated (requires valid authentication)

    Query Parameters:
        - q (str, optional): Search query to filter users by full_name, nickname, or email

    Search Logic:
        The search is case-insensitive and matches partial strings in:
        - full_name (contains search term)
        - nickname (contains search term)
        - email (contains search term)

    Returns:
        200: List of users (public information only)
        401: Authentication required

    Note:
        Returns only public user information for privacy and security.
    """
    # Get search query parameter
    q = request.query_params.get("q")

    # Start with all users, ordered by ID for consistent pagination
    qs = User.objects.all().order_by("id")

    # Apply search filter if query provided
    if q:
        # Search across multiple fields using OR logic
        qs = (
            qs.filter(full_name__icontains=q)
            | qs.filter(nickname__icontains=q)
            | qs.filter(email__icontains=q)
        )

    # Return only public user information
    return Response(PublicUserSerializer(qs, many=True).data)
