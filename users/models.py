from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from dashboard.models import Institution

class UserProfile(models.Model):
    """Extended user profile for organization users"""
    USER_ROLES = [
        ('admin', 'Administrator'),
        ('manager', 'Farm Manager'),
        ('analyst', 'Data Analyst'),
        ('viewer', 'Viewer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Activation'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone_number = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Permissions (granular control)
    can_manage_farms = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_generate_reports = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    can_access_api = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_users')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    def update_permissions_from_role(self):
        """Set permissions based on role"""
        role_permissions = {
            'admin': {
                'can_manage_farms': True,
                'can_manage_users': True,
                'can_generate_reports': True,
                'can_export_data': True,
                'can_access_api': True,
                'can_manage_settings': True,
            },
            'manager': {
                'can_manage_farms': True,
                'can_manage_users': False,
                'can_generate_reports': True,
                'can_export_data': True,
                'can_access_api': False,
                'can_manage_settings': False,
            },
            'analyst': {
                'can_manage_farms': False,
                'can_manage_users': False,
                'can_generate_reports': True,
                'can_export_data': True,
                'can_access_api': False,
                'can_manage_settings': False,
            },
            'viewer': {
                'can_manage_farms': False,
                'can_manage_users': False,
                'can_generate_reports': False,
                'can_export_data': False,
                'can_access_api': False,
                'can_manage_settings': False,
            },
        }
        
        permissions = role_permissions.get(self.role, role_permissions['viewer'])
        for perm, value in permissions.items():
            setattr(self, perm, value)
        
        # Also update Django groups
        group_name = dict(self.USER_ROLES).get(self.role, 'Viewer')
        group, _ = Group.objects.get_or_create(name=group_name)
        self.user.groups.clear()
        self.user.groups.add(group)


class UserActivity(models.Model):
    """Track user activity"""
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('report', 'Report Generation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"


# users/models.py

class UserSession(models.Model):
    """Track active user sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    device = models.CharField(max_length=100, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.device}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)