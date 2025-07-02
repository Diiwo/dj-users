from django.contrib.auth.models import AbstractBaseUser


def update_user_profile(
    user: AbstractBaseUser,
    data: dict
) -> AbstractBaseUser:
    for attr, value in data.items():
        setattr(user, attr, value)
    user.save()
    return user
