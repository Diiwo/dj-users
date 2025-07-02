from django.urls import include, path
from rest_framework.routers import DefaultRouter
from dj_users.presentation.v1.viewsets import (
    UserViewSet,
    ProfileViewSet,
)
from dj_users.presentation.v1.viewsets import (
    RegisterUserAPIView,
    DoctorAgendaAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('user', UserViewSet, basename='user')
router.register('profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    # APIView
    path('api/v1/register/', RegisterUserAPIView.as_view(), name='register_user'),
    path(
        route='api/v1/doctors/agenda/<uuid:token>/',
        view=DoctorAgendaAPIView.as_view(),
        name='doctor_agenda'
    ),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
