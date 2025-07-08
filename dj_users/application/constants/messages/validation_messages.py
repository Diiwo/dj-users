# ======================================================================
# VALIDATION MESSAGES
# ======================================================================
from django.utils.translation import gettext_lazy as _

EMAIL_ALREADY_EXISTS = _("Este correo ya se encuentra en uso por otro usuario.")
USERNAME_ALREADY_EXISTS = _("Este nombre de usuario ya se encuentra en uso por otro usuario.")
CURRENT_PASSWORD_INCORRECT = _("La contraseña actual es incorrecta.")
PASSWORDS_NOT_MATCH = _("Las contraseñas no coinciden")
ONLY_ADMIN_CAN_REGISTER_PROFILES = _("Solo usuarios administradores pueden registrar un perfil.")
ROL_NOT_PERMITED = _("Rol no permitido.")
