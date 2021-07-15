from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from authentication.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_active')
    filter_horizontal = ('groups', 'user_permissions')
    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('date_joined',)
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}),
    )
    ordering = ('email',)
    search_fields = ('email',)

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            self.readonly_fields = ('date_joined', 'is_superuser', 'user_permissions', 'groups',)
        else:
            self.readonly_fields = ('date_joined',)
        return True
