from django.contrib.auth.models import AbstractBaseUser


def has_admin_privileges(user: AbstractBaseUser):
    return user and (user.is_staff or user.is_superuser)
