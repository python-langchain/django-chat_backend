from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.indexes import GinIndex


# Custom User Models and Manager
# This module defines a custom User model with email-based authentication
# and a custom UserManager for handling user creation and management


class UserManager(BaseUserManager):
    """
    Custom User Manager that extends Django's BaseUserManager.
    Handles the creation of regular users and superusers with email-based authentication.
    """

    """
    Custom User Manager that extends Django's BaseUserManager.
    Handles the creation of regular users and superusers with email-based authentication.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Private method to create and save a user with the given email and password.

        Args:
            email (str): User's email address (used as username)
            password (str): User's password
            **extra_fields: Additional fields to set on the user

        Returns:
            User: The created user instance

        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email (str): User's email address
            password (str, optional): User's password
            **extra_fields: Additional fields to set on the user

        Returns:
            User: The created user instance
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Args:
            email (str): Superuser's email address
            password (str): Superuser's password
            **extra_fields: Additional fields to set on the superuser

        Returns:
            User: The created superuser instance

        Raises:
            ValueError: If is_staff or is_superuser is not True
        """
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email (str): Superuser's email address
            password (str): Superuser's password
            **extra_fields: Additional fields to set on the superuser
            
        Returns:
            User: The created superuser instance
            
        Raises:
            ValueError: If is_staff or is_superuser is not True
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that extends Django's AbstractBaseUser and PermissionsMixin.
    Uses email as the unique identifier instead of username.

    Features:
    - Email-based authentication
    - Role-based access control (User/Admin)
    - Flexible user information storage with JSONField
    - Full name and nickname support
    - PostgreSQL GIN index for efficient JSON queries
    """

    class Roles(models.TextChoices):
        """
        Enumeration of available user roles.
        """

        USER = "user", "User"
        ADMIN = "admin", "Admin"

    # Core user identification fields
    email = models.EmailField(unique=True)  # Primary identifier for authentication
    full_name = models.CharField(max_length=255)  # User's complete name
    nickname = models.CharField(max_length=100, blank=True)  # Optional display name
    role = models.CharField(
        max_length=10, choices=Roles.choices, default=Roles.USER
    )  # User role for permissions

    # Flexible storage for additional user information
    other_info = models.JSONField(
        default=dict, blank=True
    )  # JSONB in Postgres for efficient storage and querying

    # Django built-in user status fields
    is_active = models.BooleanField(default=True)  # Whether the user account is active
    is_staff = models.BooleanField(default=False)  # Whether user can access admin site
    date_joined = models.DateTimeField(auto_now_add=True)  # Account creation timestamp

    # Connect the custom manager
    objects = UserManager()

    # Configure authentication settings
    USERNAME_FIELD = "email"  # Use email for authentication instead of username
    REQUIRED_FIELDS = []  # No additional required fields for superuser creation

    class Meta:
        """
        Meta options for the User model.
        Defines database indexes for optimal performance.
        """

        indexes = [
            # GIN index for efficient JSON field queries in PostgreSQL
            GinIndex(fields=["other_info"], name="users_other_info_gin"),
        ]

    def __str__(self):
        """
        String representation of the User object.

        Returns:
            str: The user's email address
        """
        return self.email
