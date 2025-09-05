from django.utils.translation import gettext_lazy as _


class UserResponseMessages:
    PASSWORD_UPDATE_SUCCESSFULLY = _("Contraseña actualizada con éxito.")
    NO_PERMISSION_TO_LIST_USERS = _("No tienes permiso para listar usuarios.")
    NO_PERMISSION_TO_CREATE_USERS_FROM_ENDPOINT = _(
        "No está permitido crear usuarios desde este endpoint."
    )


class RegistrationResponseMessages:
    USER_SUCCESSFULLY_REGISTERED = _("Usuario registrado con éxito.")


class ProfileResponseMessages:
    NO_PERMISSION_TO_LIST_PROFILES = _("No tienes permiso para listar perfiles.")


class AdminResponseMessages:
    SHOULD_SEND_PARAMETER_USER_TYPE = _("Debes proporcionar el parámetro `user_type`")


class ResponseMessages:
    User = UserResponseMessages
    Registration = RegistrationResponseMessages
    Profile = ProfileResponseMessages
    Admin = AdminResponseMessages
