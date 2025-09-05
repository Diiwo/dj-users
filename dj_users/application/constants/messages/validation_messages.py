# ======================================================================
# VALIDATION MESSAGES
# ======================================================================
from django.utils.translation import gettext_lazy as _


class UserValidationMessages:
    EMAIL_ALREADY_EXISTS = _("Este correo ya se encuentra en uso por otro usuario.")
    USERNAME_ALREADY_EXISTS = _(
        "Este nombre de usuario ya se encuentra en uso por otro usuario."
    )


class PasswordValidationMessages:
    PASSWORDS_NOT_MATCH = _("Las contraseñas no coinciden")
    CURRENT_PASSWORD_INCORRECT = _("La contraseña actual es incorrecta.")


class RegistrationValidationMessages:
    ROL_CREATION_NO_VALID = _(
        "El rol proporcionado no tiene un tipo de perfil correspondiente "
        "o no es un rol válido para el registro."
    )


class PermissionsValidationMessages:
    ROL_NOT_PERMITED = _("Rol no permitido.")


class ValidationMessages:
    User = UserValidationMessages
    Password = PasswordValidationMessages
    Registration = RegistrationValidationMessages
    Permissions = PermissionsValidationMessages
