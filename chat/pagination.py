"""
Custom pagination classes for chat application API responses.

This module defines pagination settings for chat-related API endpoints
to ensure consistent and efficient data retrieval patterns.
"""

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """
    Default pagination configuration for chat API endpoints.
    
    Provides standardized pagination settings with reasonable defaults
    for chat messages and other paginated responses.
    
    Settings:
        - page_size: Default number of items per page (25)
        - page_size_query_param: URL parameter to customize page size
        - max_page_size: Maximum allowed items per page (100)
    """
    # Default number of items returned per page
    page_size = 25
    
    # Query parameter name for clients to customize page size
    # Usage: ?page_size=50
    page_size_query_param = "page_size"
    
    # Maximum number of items allowed per page (prevents abuse)
    max_page_size = 100
