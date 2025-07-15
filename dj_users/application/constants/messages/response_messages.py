from django.utils.translation import gettext_lazy as _


class ResponseMessages:
    """
    Contains all API response messages,
    organized by their respective contexts or Views.
    """

    class User:
        PASSWORD_UPDATE_SUCCESSFULLY = _("Contraseña actualizada con éxito.")
        NO_PERMISSION_TO_LIST_USERS = _("No tienes permiso para listar usuarios.")
        NO_PERMISSION_TO_CREATE_USERS_FROM_ENDPOINT = _(
            "No está permitido crear usuarios desde este endpoint."
        )

    class Registration:
        USER_SUCCESSFULLY_REGISTERED = _("Usuario registrado con éxito.")

    class Profile:
        NO_PERMISSION_TO_LIST_PROFILES = _("No tienes permiso para listar perfiles.")

    class Admin:
        SHOULD_SEND_PARAMETER_USER_TYPE = _("Debes proporcionar el parámetro `user_type`")
