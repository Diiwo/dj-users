# ======================================================================
# Imports
# ======================================================================
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_users.application.domain.roles import UserRole

from dj_users.application.logic.change_password import change_user_password
from dj_users.application.logic.register_user import register_user
from dj_users.application.logic.update_user import update_user

from dj_users.application.constants.messages.response_messages import ResponseMessages
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
    http_method_names = ['get', 'patch', 'post', 'head', 'options']

    serializer_class = UserSerializer

    action_serializer_classes = {
        'partial_update': UserUpdateSerializer,
        'update': UserUpdateSerializer,
        'list': UserSerializer,
        'retrieve': UserSerializer,
        # Custom actions
        'change_password': {
            'post': ChangePasswordSerializer
        },
        'my_user': {
            'get': UserSerializer,
            'patch': UserUpdateSerializer,
        },
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

        updated_user = update_user(
            user=self.request.user,
            data=serializer.validated_data
        )
        return Response(self.get_serializer(updated_user).data)

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": ResponseMessages.User.NO_PERMISSION_TO_LIST_USERS},
            status=status.HTTP_403_FORBIDDEN
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": ResponseMessages.User.NO_PERMISSION_TO_CREATE_USERS_FROM_ENDPOINT},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, methods=['post'], url_path='change-password', url_name='change_password')
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        change_user_password(
            user=request.user,
            new_password=serializer.validated_data['new_password']
        )
        return Response(
            data={"detail": ResponseMessages.User.PASSWORD_UPDATE_SUCCESSFULLY},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get', 'patch'], url_path='me', url_name='my_user')
    def my_user(self, request):
        instance = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            updated_user = update_user(
                user=self.request.user,
                data=serializer.validated_data
            )
            return Response(self.get_serializer(updated_user).data)


# ======================================================================
# ProfileViewSet - profile view by user type
# ======================================================================


class AdminClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProfileViewSet(
    ActionSerializerMixin,
    UniversalStateQuerysetMixin,
    viewsets.ModelViewSet
):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']

    role_map = {
        UserRole.DOCTOR: (DoctorProfile, DoctorProfileSerializer),
        UserRole.PATIENT: (PatientProfile, PatientProfileSerializer),
        UserRole.NURSE: (NurseProfile, NurseProfileSerializer),
    }

    def get_queryset(self):
        role = self.request.user.user_type

        if role == UserRole.ADMIN:
            return CustomUser.objects.filter(pk=self.request.user.pk)
        else:
            model = self.role_map[role][0]
            return model.objects.filter(user=self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    def get_serializer_class(self):
        role = self.request.user.user_type

        if role == UserRole.ADMIN:
            return UserUpdateSerializer
        return self.role_map[role][1]

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": ResponseMessages.Profile.NO_PERMISSION_TO_LIST_PROFILES},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['get', 'patch'], url_path='me', url_name='my_profile')
    def my_profile(self, request):
        instance = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class AdminUserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    filterset_fields = ['user__user_type', 'specialty']

    model_map = {
        'doctor': (DoctorProfile, DoctorProfileSerializer),
        'patient': (PatientProfile, PatientProfileSerializer),
        'nurse': (NurseProfile, NurseProfileSerializer),
    }

    def _get_model_and_serializer(self):
        profile_type = self.request.query_params.get('user_type')
        if not profile_type:
            return None

        model_serializer = self.model_map.get(profile_type.lower())
        if not model_serializer:
            return None

        return model_serializer

    def get_queryset(self):
        model_serializer = self._get_model_and_serializer()
        if not model_serializer:
            return DoctorProfile.objects.none()
        (model, _) = model_serializer
        return model.objects.filter(universal_state='active')

    def get_serializer_class(self):
        model_serializer = self._get_model_and_serializer()
        if not model_serializer:
            return DoctorProfileSerializer
        (_, serializer) = model_serializer
        return serializer

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('user_type'):
            return Response(
                {
                    "detail": (
                        ResponseMessages.Admin.SHOULD_SEND_PARAMETER_USER_TYPE
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)


# ======================================================================
# APIView public (registration, query by token)
# ======================================================================


class RegisterUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_user(
            serializer.validated_data
        )

        return Response({
            "detail": ResponseMessages.Registration.USER_SUCCESSFULLY_REGISTERED,
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class DoctorAgendaAPIView(APIView):
    permission_classes = []

    def get(self, request, token):
        doctor = get_object_or_404(DoctorProfile, user__agenda_token=token)
        serializer = DoctorProfileSerializer(doctor)
        return Response(serializer.data)
