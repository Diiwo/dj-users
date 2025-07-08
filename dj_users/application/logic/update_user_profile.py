from dj_users.infrastructure.models import CustomUser


def update_user_profile(user: CustomUser, data: dict) -> CustomUser:
    """
    Updates the fields of the base user profile (CustomUser).

    Args:
    user (CustomUser): Authenticated user.
    data (dict): Fields to update (e.g., username, email, etc.).

    Returns:
    CustomUser: Updated user.
    """
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.save()
    return user
