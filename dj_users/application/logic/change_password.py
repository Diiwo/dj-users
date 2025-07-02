from django.contrib.auth.models import AbstractBaseUser


def change_user_password(user: AbstractBaseUser, new_password: str):
    user.set_password(new_password)
    user.save()
    return user
