from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_users.application.logic.change_password import change_user_password
from dj_users.application.domain.roles import UserRole
from dj_users.application.logic.register_user import register_user
from dj_users.application.logic.user_profile import update_user_profile
from dj_users.infrastructure.models import (
    CustomUser,
    DoctorProfile,
    PatientProfile,
    NurseProfile
)
from .serializers import (
    UserSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer,
    NurseProfileSerializer,
    ChangePasswordSerializer,
    RegisterUserSerializer
)

ACTION_READ = ('list', 'retrieve')
ACTION_UPDATE = ('update', 'partial_update')


class UniversalStateModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet base que hace soft-delete y filtra por universal_state=active
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.model, 'universal_state'):
            return queryset.filter(universal_state='active')
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'universal_state'):
            instance.universal_state = 'terminated'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)


# ======================================================================
# ModeViewSet
# ======================================================================


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        change_user_password(
            user=request.user,
            new_password=serializer.validated_data['new_password']
        )

        return Response(
            data={"detail": "Contraseña actualizada correctamente."},
            status=status.HTTP_200_OK
        )


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


# ======================================================================
# APIView
# ======================================================================


class RegisterUserAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_user(serializer.validated_data, request_user=request.user)

        return Response({
            "detail": "Usuario registrado correctamente.",
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class DoctorAgendaAPIView(APIView):
    permission_classes = []

    def get(self, request, token):
        doctor = get_object_or_404(DoctorProfile, user__agenda_token=token)
        serializer = DoctorProfileSerializer(doctor)
        return Response(serializer.data)
