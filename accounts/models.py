from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class Institution(models.Model):
    INSTITUTION_TYPES = [
        ('government', 'Government Agency'),
        ('ngo', 'Non-Governmental Organization'),
        ('cooperative', 'Farmer Cooperative'),
        ('private', 'Private Company'),
        ('research', 'Research Institution'),
        ('association', 'Farmers Association'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    institution_type = models.CharField(max_length=50, choices=INSTITUTION_TYPES)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    street = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    clusters_count = models.IntegerField(
        default=1, 
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.institution_type})"
    
    def generate_verification_token(self):
        import secrets
        self.verification_token = secrets.token_urlsafe(32)
        self.save()
        return self.verification_token

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('analyst', 'Data Analyst'),
        ('viewer', 'Viewer'),
        ('field_agent', 'Field Agent'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    pin = models.CharField(max_length=6, blank=True, null=True)  # 6-digit PIN
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Login History"
        verbose_name_plural = "Login History"
        ordering = ['-login_time']
    
    def __str__(self):
        status = "Success" if self.success else f"Failed: {self.failure_reason}"
        return f"{self.user.username} - {self.login_time} - {status}"

class OTP(models.Model):
    OTP_TYPES = [
        ('pin_reset', 'PIN Reset'),
        ('email_verification', 'Email Verification'),
        ('login', 'Two-Factor Login'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.otp_type} - {self.code}"
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

class SecuritySettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor_enabled = models.BooleanField(default=False)
    login_notifications = models.BooleanField(default=True)
    session_timeout = models.IntegerField(default=30)  # in minutes
    max_login_attempts = models.IntegerField(default=5)
    password_changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Security Settings"
        verbose_name_plural = "Security Settings"
    
    def __str__(self):
        return f"Security Settings - {self.user.username}"

class EmailTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('welcome', 'Welcome Email'),
        ('pin_reset', 'PIN Reset'),
        ('verification', 'Email Verification'),
        ('login_notification', 'Login Notification'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    

