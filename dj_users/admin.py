from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, DoctorProfile, NurseProfile, PatientProfile


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('phone_number', 'birth_date')}),
        (_('Role info'), {'fields': ('user_type',)}),
        (_('Agenda'), {'fields': ('agenda_token',)}),
        (_('Email confirmation'), {'fields': ('confirmation_token', 'is_email_confirmed')}),
        (_('Estado general'), {'fields': ('universal_state', 'object_locked', 'lock_type')}),
        (_('Audit info'), {'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

    list_display = ('id', 'username', 'email', 'user_type', 'is_email_confirmed', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'user_type', 'is_email_confirmed')
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'confirmation_token', 'agenda_token'
    )
    actions = ['set_active', 'set_frozen', 'set_terminated']

    def set_active(self, request, queryset):
        queryset.update(universal_state='active')
    set_active.short_description = 'Marcar como ACTIVE'

    def set_frozen(self, request, queryset):
        queryset.update(universal_state='frozen')
    set_frozen.short_description = 'Marcar como FROZEN'

    def set_terminated(self, request, queryset):
        queryset.update(universal_state='terminated')
    set_terminated.short_description = 'Marcar como TERMINATED'


admin.site.register(DoctorProfile)
admin.site.register(NurseProfile)
admin.site.register(PatientProfile)
