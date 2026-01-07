from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Institution, UserProfile, LoginHistory, OTP, SecuritySettings, EmailTemplate

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 
        'first_name', 'last_name', 
        'is_staff', 'get_institution', 'get_role'
    )
    list_filter = (
        'is_staff', 'is_superuser', 
        'is_active', 'userprofile__institution'
    )

    def get_institution(self, obj):
        # Ensure userprofile exists
        userprofile = getattr(obj, 'userprofile', None)

        if userprofile and userprofile.institution:
            return userprofile.institution.name
        return "No Institution"
    get_institution.short_description = 'Institution'

    def get_role(self, obj):
        userprofile = getattr(obj, 'userprofile', None)

        if userprofile and userprofile.role:
            return userprofile.role
        return "No Role"
    get_role.short_description = 'Role'

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution_type', 'country', 'is_verified', 'created_at')
    list_filter = ('institution_type', 'country', 'is_verified')
    search_fields = ('name', 'email', 'registration_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'institution_type', 'registration_number')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'country', 'constituency', 'ward', 'street')
        }),
        ('Account Settings', {
            'fields': ('clusters_count', 'is_verified', 'verification_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'role', 'is_active', 'email_verified')
    list_filter = ('role', 'is_active', 'email_verified', 'institution')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('date_joined', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'institution', 'role')
        }),
        ('Contact Details', {
            'fields': ('phone', 'profile_picture', 'job_title', 'department')
        }),
        ('Security', {
            'fields': ('pin', 'email_verified', 'last_login_ip')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address', 'success', 'failure_reason')
    list_filter = ('success', 'login_time')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('login_time',)
    date_hierarchy = 'login_time'

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_type', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('otp_type', 'is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('created_at',)

@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'two_factor_enabled', 'login_notifications', 'max_login_attempts')
    list_filter = ('two_factor_enabled', 'login_notifications')
    search_fields = ('user__username', 'user__email')

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active')
    search_fields = ('name', 'subject', 'body')
    readonly_fields = ('created_at', 'updated_at')

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)