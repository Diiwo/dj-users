
from rest_framework import serializers

from dj_users.application.constants.messages import validation_messages
from dj_users.application.domain.roles import UserRole
from dj_users.infrastructure.models import (
    CustomUser,
    DoctorProfile,
    PatientProfile,
    NurseProfile,
    Clinic
)


# ======================================================================
# Base Serializers (ModelSerializers simples)
# ======================================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'phone_number', 'birth_date']
        read_only_fields = ['id', 'user_type']


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'
        read_only_fields = ['id']


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ['id', 'agenda_token']


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['id']


class NurseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseProfile
        fields = '__all__'
        read_only_fields = ['id']


# ======================================================================
# Input Serializers (Para escritura: create/update/patch)
# ======================================================================

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'birth_date']
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                validation_messages.EMAIL_ALREADY_EXISTS
            )
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(
               validation_messages.USERNAME_ALREADY_EXISTS
            )
        return value


# ======================================================================
# Auth & Account Serializers (Registro, cambio de contraseña, etc.)
# ======================================================================

class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserRole.choices)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                validation_messages.EMAIL_ALREADY_EXISTS
            )
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                validation_messages.USERNAME_ALREADY_EXISTS
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                validation_messages.CURRENT_PASSWORD_INCORRECT
            )
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({
                "confirm_new_password": validation_messages.PASSWORDS_NOT_MATCH
            })
        return attrs
