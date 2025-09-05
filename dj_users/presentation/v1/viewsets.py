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
from django.db.models import Q

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
from dj_core_utils.db.mixins import UniversalState

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
    
    # Add filtering and search capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'username']
    filterset_fields = ['user_type', 'is_active', 'is_staff']
    ordering_fields = ['date_joined', 'last_login', 'first_name', 'last_name']
    ordering = ['-date_joined']

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
        user = self.request.user
        
        # Admin can see all users
        if user.user_type == UserRole.ADMIN:
            return CustomUser.objects.all()
        # Doctor can see patients and other doctors
        elif user.user_type == UserRole.DOCTOR:
            return CustomUser.objects.filter(
                Q(user_type__in=[UserRole.PATIENT, UserRole.DOCTOR]) |
                Q(pk=user.pk)
            )
        # Regular users can only see themselves
        else:
            return CustomUser.objects.filter(pk=user.pk)

    def get_object(self):
        # For detail views, return the requested object if user has permission
        if hasattr(self, 'kwargs') and 'pk' in self.kwargs:
            pk = self.kwargs['pk']
            return self.get_queryset().get(pk=pk)
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
        # Only admins and doctors can list users
        if request.user.user_type not in [UserRole.ADMIN, UserRole.DOCTOR]:
            return Response(
                {"detail": ResponseMessages.User.NO_PERMISSION_TO_LIST_USERS},
                status=status.HTTP_403_FORBIDDEN
            )

        # Use the default list implementation with our filtered queryset
        return super().list(request, *args, **kwargs)

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

    @action(detail=False, methods=['get'], url_path='my_data', url_name='my_data')
    def my_data(self, request):
        """Get current user data for frontend auth service"""
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats', url_name='user_stats')
    def user_stats(self, request):
        """Get user statistics - available for admins and doctors"""
        user = request.user

        # Only admins and doctors can access stats
        if user.user_type not in [UserRole.ADMIN, UserRole.DOCTOR]:
            return Response(
                {"detail": "No tienes permisos para ver estadísticas"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get accessible users based on role
        accessible_users = self.get_queryset()

        # Calculate stats
        stats = {
            'total_users': accessible_users.count(),
            'total_patients': accessible_users.filter(user_type=UserRole.PATIENT).count(),
            'total_doctors': accessible_users.filter(user_type=UserRole.DOCTOR).count(),
            'total_nurses': accessible_users.filter(user_type=UserRole.NURSE).count(),
            'total_admins': accessible_users.filter(
                user_type=UserRole.ADMIN
            ).count() if user.user_type == UserRole.ADMIN else 0,
            'active_users': accessible_users.filter(is_active=True).count(),
            'inactive_users': accessible_users.filter(is_active=False).count(),
        }

        return Response(stats, status=status.HTTP_200_OK)


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
        return model.objects.filter(universal_state=UniversalState.ACTIVE)

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

    @action(detail=False, methods=['get'], url_path='stats', url_name='profile_stats')
    def profile_stats(self, request):
        """Get profile statistics for admin users"""
        stats = {
            'total_doctor_profiles': DoctorProfile.objects.filter(
                universal_state=UniversalState.ACTIVE
            ).count(),
            'total_patient_profiles': PatientProfile.objects.filter(
                universal_state=UniversalState.ACTIVE
            ).count(),
            'total_nurse_profiles': NurseProfile.objects.filter(
                universal_state=UniversalState.ACTIVE
            ).count(),
            'total_profiles': (
                DoctorProfile.objects.filter(universal_state=UniversalState.ACTIVE).count() +
                PatientProfile.objects.filter(universal_state=UniversalState.ACTIVE).count() +
                NurseProfile.objects.filter(universal_state=UniversalState.ACTIVE).count()
            )
        }

        return Response(stats, status=status.HTTP_200_OK)


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
