import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from dj_users.application.constants.blood_types import BLOOD_TYPES
from dj_users.application.domain.roles import UserRole

from dj_core_utils.db.models import CoreBaseModel


class CustomUser(AbstractUser, CoreBaseModel):
    imagen = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    agenda_token = models.UUIDField(default=uuid.uuid4, unique=True)
    confirmation_token = models.UUIDField(default=uuid.uuid4)
    is_email_confirmed = models.BooleanField(default=False)
    birth_date = models.DateField(null=True, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT
    )

    class Meta:
        app_label = 'dj_users'
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return f'{self.username}'


class Clinic(CoreBaseModel):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class DoctorProfile(CoreBaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_data'
    )
    specialty = models.ForeignKey(
        "dj_catalogs.Specialty",
        on_delete=models.PROTECT,
        null=True
    )
    license_number = models.CharField(max_length=50)
    kit_accepted = models.BooleanField(default=False)
    professional_license = models.CharField(max_length=50)
    verificated = models.BooleanField(default=False)
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.SET_NULL,
        null=True,
        related_name='doctors'
    )

    def __str__(self):
        return _('Dr. %(fullname)s') % {'fullname': self.user.get_full_name()}

    class Meta:
        app_label = 'dj_users'
        verbose_name = _('Perfil de médico')


class PatientProfile(CoreBaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='patient_data'
    )
    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_TYPES,
        blank=True
    )

    class Meta:
        app_label = 'dj_users'
        verbose_name = _('Perfil de paciente')
        verbose_name_plural = _('Perfil de pacientes')

    def __str__(self):
        return _('Paciente: %(username)s') % {'username': self.user.username}


class NurseProfile(CoreBaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='nurse_data')
    available_services = models.TextField(blank=True)

    class Meta:
        app_label = 'dj_users'
        verbose_name = _('Perfil de enfermera')
        verbose_name_plural = _('Perfil de enfermeras')

    def __str__(self):
        return _('Enfermero: %(username)s') % {'username': self.user.username}
