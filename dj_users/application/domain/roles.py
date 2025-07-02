from django.db import models


class UserRole(models.TextChoices):
    PATIENT = 'patient', 'Paciente'
    DOCTOR = 'doctor', 'Médico'
    NURSE = 'nurse', 'Enfermero/a'
    ADMIN = 'admin', 'Administrador'
