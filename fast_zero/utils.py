def serialize_user(user) -> dict:
    """
    Serialize a user object to a dictionary.
    """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'is_superuser': user.is_superuser,
        'is_verified': user.is_verified,
    }
