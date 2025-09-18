from rest_framework import serializers
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with full field access.

    This serializer is used for user creation and full user data operations.
    It includes password handling with proper security measures.

    Features:
    - Password validation (minimum 6 characters)
    - Password write-only security
    - Role and date_joined fields are read-only for security
    - Proper password hashing on user creation
    """

    # Password field with security constraints
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    # Password field with security constraints
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "full_name",
            "nickname",
            "role",
            "other_info",
            "date_joined",
        ]
        # Security: Prevent modification of sensitive fields
        read_only_fields = ["id", "date_joined", "role"]  # role can be set by admins

    def create(self, validated_data):
        """
        Create a new user instance with properly hashed password.

        Args:
            validated_data (dict): Validated user data from the serializer

        Returns:
            User: The newly created user instance

        Note:
            The password is properly hashed using Django's set_password method
            before saving to ensure security.
        """
        # Extract password to handle separately
        password = validated_data.pop("password")

        # Create user instance without password
        user = User(**validated_data)

        # Hash and set the password securely
        user.set_password(password)
        user.save()

        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serializer for public user information.

    This serializer exposes only safe, non-sensitive user information
    that can be shared publicly or with other users.

    Used for:
    - User listings
    - Public profiles
    - Search results
    - Any context where sensitive data should not be exposed
    """

    class Meta:
        model = User
        # Only include safe, public fields
        fields = ["id", "email", "full_name", "nickname"]
