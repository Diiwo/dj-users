from dj_users.infrastructure.models import CustomUser


def update_user(user: CustomUser, data: dict) -> CustomUser:
    """
    Updates the fields of the base user profile (CustomUser), including the image.
    It explicitly excludes fields like 'password' or those marked as read-only
    by the serializer.

    Args:
    user (CustomUser): Authenticated user instance to be updated.
    data (dict): Fields to update (e.g., username, email, image, etc.),
                 as validated by the serializer.

    Returns:
    CustomUser: Updated user instance.
    """
    image = data.pop('image', None)
    if image is not None:
        user.image = image

    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.save()
    return user
