from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied

from dj_users.infrastructure.models import (
    DoctorProfile, PatientProfile, NurseProfile
)
from dj_users.application.domain.roles import UserRole
from dj_users.application.utils.privileges import has_admin_privileges


User = get_user_model()


def register_user(validated_data: dict, request_user=None):
    role = validated_data['role']
    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    if role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.PATIENT]:
        if not has_admin_privileges(request_user):
            raise PermissionDenied(
                "Solo usuarios administradores pueden registrar un perfil."
            )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        user_type=role
    )

    profile_model_map = {
        UserRole.DOCTOR: DoctorProfile,
        UserRole.PATIENT: PatientProfile,
        UserRole.NURSE: NurseProfile
    }

    profile_model = profile_model_map.get(role)
    if profile_model:
        profile_model.objects.create(user=user)

    return user
