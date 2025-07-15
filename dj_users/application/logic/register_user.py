from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from dj_users.application.constants.messages.validation_messages import ValidationMessages
from dj_users.application.domain.roles import UserRole
from dj_users.infrastructure.models import (
    CustomUser,
    DoctorProfile,
    NurseProfile,
    PatientProfile,
)

User = get_user_model()


def register_user(validated_data: dict) -> CustomUser:
    # Required additional fields
    # We use pop to remove them and pass the rest to create_user
    role = validated_data.pop('role')
    username = validated_data.pop('username')
    email = validated_data.pop('email')
    password = validated_data.pop('password')

    # The remaining fields in validated_data are optional and can be passed directly
    # to create_user if your CustomUser.objects.create_user supports it (which is common)
    # or assigned later.

    with transaction.atomic():
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=role,
            **validated_data
        )

        # If create_user doesn't accept those fields directly, do it like this:
        # user = CustomUser.objects.create_user(
        #     username=username,
        #     email=email,
        #     password=password,
        #     user_type=role
        # )
        # # Assign optional fields after creation
        # for field, value in validated_data.items():
        #     if hasattr(user, field) and value is not None:
        #         setattr(user, field, value)
        # user.save() # Save changes if you assigned fields afterwards

        profile_model_map = {
            UserRole.DOCTOR: DoctorProfile,
            UserRole.PATIENT: PatientProfile,
            UserRole.NURSE: NurseProfile
        }

        if role not in profile_model_map and role not in [UserRole.ADMIN, UserRole.STAFF]:
            raise ValidationError(
                ValidationMessages.Registration.ROL_CREATION_NO_VALID
            )

        profile_model = profile_model_map.get(role)
        if profile_model:
            profile_model.objects.create(user=user)

    return user
