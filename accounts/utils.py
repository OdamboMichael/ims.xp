# Add these utility functions at the TOP or BOTTOM of your utils.py file

import random
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP, EmailTemplate, SecuritySettings, LoginHistory, UserProfile

# OTP utility functions
def create_otp_record(user, otp_type, ip_address=None):
    """
    Create an OTP record for the user
    """
    from django.utils import timezone
    
    # Generate a 6-digit OTP
    code = str(random.randint(100000, 999999))
    
    # Set expiration (10 minutes from now)
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Create OTP record
    otp = OTP.objects.create(
        user=user,
        otp_type=otp_type,
        code=code,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    return otp

def verify_otp(user, code, otp_type):
    """
    Verify an OTP code
    """
    from django.utils import timezone
    
    try:
        otp = OTP.objects.filter(
            user=user,
            otp_type=otp_type,
            is_used=False
        ).latest('created_at')
        
        if otp.code == code and not otp.is_used and timezone.now() < otp.expires_at:
            otp.is_used = True
            otp.save()
            return True
        return False
    except OTP.DoesNotExist:
        return False

# Email utility function
def send_email_template(template_type, user, context=None):
    """
    Send an email using a template
    """
    try:
        template = EmailTemplate.objects.get(template_type=template_type, is_active=True)
        
        if context is None:
            context = {}
        
        # Add user to context
        context['user'] = user
        
        # Format subject and body with context
        subject = template.subject.format(**context)
        body = template.body.format(**context)
        
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except EmailTemplate.DoesNotExist:
        # Fallback to default email
        send_mail(
            subject="Notification from IMS",
            message=f"Hello {user.username},\n\nThis is a notification from the IMS system.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Security utility functions
def get_security_settings(user):
    """
    Get or create security settings for a user
    """
    settings, _ = SecuritySettings.objects.get_or_create(user=user)
    return settings

def check_login_attempts(user):
    """
    Check if user has exceeded max login attempts
    """
    from django.utils import timezone
    from .models import LoginHistory
    
    security_settings = get_security_settings(user)
    
    # Get failed login attempts in last 30 minutes
    thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
    failed_attempts = LoginHistory.objects.filter(
        user=user,
        success=False,
        login_time__gte=thirty_minutes_ago
    ).count()
    
    return failed_attempts >= security_settings.max_login_attempts