"""
Utility functions for chat application.

This module contains helper functions used throughout the chat system
for common operations like generating unique identifiers.
"""

import hashlib


def pair_key_for_users(a_id: int, b_id: int) -> str:
    """
    Generate a unique, deterministic key for a pair of users.
    
    Creates a consistent hash-based identifier for any two users regardless
    of the order they're provided. This ensures that a chat between user A
    and user B has the same key as a chat between user B and user A.
    
    Args:
        a_id (int): ID of the first user
        b_id (int): ID of the second user
        
    Returns:
        str: SHA256 hash string that uniquely identifies this user pair
        
    Example:
        >>> pair_key_for_users(1, 2)
        'abc123...'  # Same result as pair_key_for_users(2, 1)
    """
    # Sort the IDs to ensure consistent ordering regardless of input order
    x, y = sorted([int(a_id), int(b_id)])
    
    # Generate a deterministic hash from the sorted pair
    return hashlib.sha256(f"pair:{x}:{y}".encode()).hexdigest()
