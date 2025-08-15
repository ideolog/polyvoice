from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models.users import User
from users.models.plans import Plan
from users.models.identities import ExternalIdentity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-date_joined',)
    list_display = (
        'id', 'email', 'plan', 'is_staff', 'is_superuser', 'last_login', 'date_joined'
    )
    search_fields = ('email',)
    list_filter = ('plan', 'is_staff', 'is_superuser', 'is_active')
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password', 'plan', 'api_key')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'plan', 'api_key'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'messages_per_minute', 'messages_per_day')
    search_fields = ('name',)
    list_filter = ('messages_per_minute', 'messages_per_day')


@admin.register(ExternalIdentity)
class ExternalIdentityAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "external_id", "username", "user", "created_at")
    search_fields = ("external_id", "username", "user__email")
    list_filter = ("provider",)
    ordering = ("-created_at",)