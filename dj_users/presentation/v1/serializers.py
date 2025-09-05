
from rest_framework import serializers

from dj_users.application.constants.messages.validation_messages import ValidationMessages
from dj_users.application.domain.roles import UserRole
from dj_users.infrastructure.models import (
    CustomUser,
    DoctorProfile,
    PatientProfile,
    NurseProfile,
    Clinic,
)


# ======================================================================
# Base Serializers (ModelSerializers simples)
# ======================================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'birth_date',
            'image',
            'is_active',
            'is_staff',
            'user_type',
            'is_email_confirmed',
            'agenda_token',
            'last_login',
            'date_joined',
            'universal_state',
            'groups',
            'user_permissions',
        ]
        read_only_fields = [
            'id',
            'user_type',
            'agenda_token',
            'is_email_confirmed',
            'is_staff',
            'is_active',
            'last_login',
            'date_joined',
            'universal_state',
            'created_at',
            'updated_at',
            'groups',
            'user_permissions',
        ]

    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                ValidationMessages.User.EMAIL_ALREADY_EXISTS
            )
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(
               ValidationMessages.User.USERNAME_ALREADY_EXISTS
            )
        return value


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'
        read_only_fields = ['id']


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
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
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number', 'birth_date',
            'first_name', 'last_name', 'image'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'birth_date': {'required': False},
        }

        read_only_fields = ['username']

    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                ValidationMessages.User.EMAIL_ALREADY_EXISTS
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
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=12, required=False)
    birth_date = serializers.DateField(required=False)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                ValidationMessages.User.EMAIL_ALREADY_EXISTS
            )
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                ValidationMessages.User.USERNAME_ALREADY_EXISTS
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
                ValidationMessages.Password.CURRENT_PASSWORD_INCORRECT
            )
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({
                "confirm_new_password": ValidationMessages.Password.PASSWORDS_NOT_MATCH
            })
        return attrs


# ======================================================================
# Custom
# ======================================================================
