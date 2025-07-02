from django.apps import AppConfig


class DjUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dj_users'
    label = 'dj_users'
    verbose_name = 'Gestión de usuarios'

    def ready(self):
        import dj_users.models  # noqa
