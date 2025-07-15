from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from dj_core_utils.db.mixins import (
    UniversalState
)

from .models import (
    Clinic,
    CustomUser,
    DoctorProfile,
    NurseProfile,
    PatientProfile,
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Fields to display in the detail/edit view of an existing user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Información personal'), {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'image',
                    'phone_number',
                    'birth_date'
                )
            }
        ),
        (_('Rol y estatus'), {'fields': ('user_type', 'is_email_confirmed')}),
        (_('Acceso y bloqueo'), {'fields': ('universal_state', 'object_locked', 'lock_type')}),
        (_('Agenda y tokens'), {'fields': ('agenda_token', 'confirmation_token')}),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
        (
            _('Información auditable'), {
                'fields': (
                    'created_at',
                    'updated_at',
                    'created_by',
                    'updated_by'
                )
            }
        ),
    )

    # Fields to be displayed when creating a NEW user from the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password',
                'password2',
                'user_type',
                'first_name',
                'last_name',
                'phone_number',
                'birth_date'
            ),
        }),
    )

    # Fields to be displayed in the user list
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'user_type', 'is_email_confirmed', 'is_staff', 'universal_state', 'is_active',
    )
    # Filters available in the sidebar
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'user_type',
        'is_email_confirmed',
        'universal_state',
    )
    # Searchable fields
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Default sorting
    ordering = ('username',)

    # Fields that cannot be edited in the detail/edit view
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'confirmation_token',
        'agenda_token',
        'last_login',
        'date_joined',
        'universal_state',
        'object_locked',
        'lock_type',
    )

    # Custom actions
    actions = ['set_active', 'set_frozen', 'set_terminated']

    def set_active(self, request, queryset):
        queryset.update(universal_state=UniversalState.ACTIVE)
    set_active.short_description = _('Marcar como ACTIVE')

    def set_frozen(self, request, queryset):
        queryset.update(universal_state=UniversalState.FROZEN)
    set_frozen.short_description = _('Marcar como FROZEN')

    def set_terminated(self, request, queryset):
        queryset.update(universal_state=UniversalState.TERMINATED)
    set_terminated.short_description = _('Marcar como TERMINATED')


admin.site.register(Clinic)
admin.site.register(DoctorProfile)
admin.site.register(NurseProfile)
admin.site.register(PatientProfile)
