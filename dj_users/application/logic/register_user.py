from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework.exceptions import PermissionDenied, ValidationError

from dj_users.application.constants.messages import validation_messages
from dj_users.application.domain.roles import UserRole
from dj_users.application.utils.privileges import has_admin_privileges
from dj_users.infrastructure.models import (
    DoctorProfile, PatientProfile, NurseProfile
)

User = get_user_model()


def register_user(validated_data: dict, request_user=None):
    role = validated_data['role']
    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    if role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.PATIENT]:
        if not has_admin_privileges(request_user):
            raise PermissionDenied(
                validation_messages.ONLY_ADMIN_CAN_REGISTER_PROFILES
            )

    with transaction.atomic():
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

        if role not in profile_model_map:
            raise ValidationError(
                validation_messages.ROL_NOT_PERMITED
            )

        profile_model = profile_model_map.get(role)
        if profile_model:
            profile_model.objects.create(user=user)

    return user
