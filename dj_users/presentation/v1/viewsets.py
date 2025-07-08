# ======================================================================
# Imports
# ======================================================================
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_users.application.logic import (
    change_password,
    register_user,
    update_user_profile,
)
from dj_users.application.domain.roles import UserRole
from dj_users.application.constants.messages import response_messages
from dj_users.infrastructure.models import (
    CustomUser,
    DoctorProfile,
    PatientProfile,
    NurseProfile,
    Clinic
)

from .serializers import (
    ClinicSerializer,
    UserSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer,
    NurseProfileSerializer,
    ChangePasswordSerializer,
    RegisterUserSerializer,
    UserUpdateSerializer,
)

from dj_core_utils.presentation.mixins import (
    ActionSerializerMixin,
    UniversalStateQuerysetMixin,
    UniversalStateSoftDeleteMixin,
)

# ======================================================================
# UserViewSet - authenticated user management
# ======================================================================


class UserViewSet(
    ActionSerializerMixin,
    UniversalStateQuerysetMixin,
    UniversalStateSoftDeleteMixin,
    viewsets.ModelViewSet
):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    action_serializer_classes = {
        'partial_update': UserUpdateSerializer,
        'update': UserUpdateSerializer,
        'change_password': ChangePasswordSerializer,
        'list': UserSerializer,
        'retrieve': UserSerializer,
    }

    def get_queryset(self):
        return CustomUser.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        update_user_profile(
            user=self.request.user,
            data=serializer.validated_data
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        change_password.change_user_password(
            user=request.user,
            new_password=serializer.validated_data['new_password']
        )
        return Response(
            data={"detail": response_messages.PASSWORD_UPDATE_SUCCESSFULLY},
            status=status.HTTP_200_OK
        )

# ======================================================================
# ProfileViewSet - profile view by user type
# ======================================================================


class AdminClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    role_map = {
        UserRole.DOCTOR: (DoctorProfile, DoctorProfileSerializer),
        UserRole.PATIENT: (PatientProfile, PatientProfileSerializer),
        UserRole.NURSE: (NurseProfile, NurseProfileSerializer),
    }

    def get_queryset(self):
        user = self.request.user
        role = user.user_type
        model = self.role_map.get(role, (DoctorProfile,))[0]
        return model.objects.filter(user=user, universal_state='active')

    def get_serializer_class(self):
        role = self.request.user.user_type
        return self.role_map.get(role, (DoctorProfile, DoctorProfileSerializer))[1]


class AdminUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    filterset_fields = ['user__user_type', 'specialty']  # specialty solo aplica a médicos

    def get_queryset(self):
        profile_type = self.request.query_params.get('user_type')
        model_map = {
            'doctor': DoctorProfile,
            'patient': PatientProfile,
            'nurse': NurseProfile,
        }
        model = model_map.get(profile_type, DoctorProfile)
        return model.objects.filter(universal_state='active')

    def get_serializer_class(self):
        profile_type = self.request.query_params.get('user_type')
        serializer_map = {
            'doctor': DoctorProfileSerializer,
            'patient': PatientProfileSerializer,
            'nurse': NurseProfileSerializer,
        }
        return serializer_map.get(profile_type, DoctorProfileSerializer)

# ======================================================================
# APIView public (registration, query by token)
# ======================================================================


class RegisterUserAPIView(APIView):
    """
    Public endpoint for registering new patient-type users.

    This endpoint does not require authentication and is designed to allow anyone
    to create a patient account.
    Other user types, such as doctors or nurses,
    can only be created by authenticated administrators within the business logic.

    Methods:
    post(request): Registers a new patient user and returns their serialized information.

    Permissions:
    Does not require authentication (permission_classes = [])
    """
    permission_classes = []

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_user.register_user(
            serializer.validated_data, request_user=request.user
        )

        return Response({
            "detail": response_messages.USER_SUCCESSFULLY_REGISTERED,
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class DoctorAgendaAPIView(APIView):
    permission_classes = []

    def get(self, request, token):
        doctor = get_object_or_404(DoctorProfile, user__agenda_token=token)
        serializer = DoctorProfileSerializer(doctor)
        return Response(serializer.data)
