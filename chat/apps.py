"""
Django application configuration for the chat app.

This module defines the configuration class for the chat application,
including settings for auto-generated primary key fields and the app name.
"""

from django.apps import AppConfig


class ChatConfig(AppConfig):
    """
    Configuration class for the chat Django application.
    
    Defines application-level settings including the default primary key
    field type and the application name for Django's app registry.
    """
    # Use BigAutoField for primary keys (supports larger ID ranges)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # The name of this application as registered in Django
    name = 'chat'
