from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Add this import
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Institution, UserProfile, OTP, LoginHistory, SecuritySettings
from .forms import (
    InstitutionRegistrationForm, CustomAuthenticationForm,
    ForgotPINForm, ResetPINForm, ProfileUpdateForm,
    UserProfileForm, SecuritySettingsForm
)
from .utils import (
    create_otp_record, send_email_template,  # Changed from send_otp_email
    get_security_settings, check_login_attempts  # Add missing imports
)

# Utility functions that should be in utils.py but we'll define here if missing
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_login_attempt(user, ip_address, user_agent, success=True, failure_reason=None):
    """Log login attempt"""
    LoginHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason
    )

def validate_pin(user, pin):
    """Validate user PIN"""
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.pin == pin
    except UserProfile.DoesNotExist:
        return False

def create_default_email_templates():
    """Create default email templates if they don't exist"""
    from .models import EmailTemplate
    
    templates = [
        {
            'name': 'Welcome Email',
            'template_type': 'welcome',
            'subject': 'Welcome to Xpert Farmer IMS, {user.username}!',
            'body': 'Hello {user.username},\n\nWelcome to Xpert Farmer IMS.\n\nYour account has been created successfully.'
        },
        {
            'name': 'PIN Reset',
            'template_type': 'pin_reset',
            'subject': 'PIN Reset OTP - Xpert Farmer IMS',
            'body': 'Hello {user.username},\n\nYour OTP for PIN reset is: {otp.code}\n\nThis OTP will expire in 10 minutes.'
        },
        {
            'name': 'Email Verification',
            'template_type': 'verification',
            'subject': 'Verify Your Email - Xpert Farmer IMS',
            'body': 'Hello {user.username},\n\nYour verification OTP is: {otp.code}\n\nThis OTP will expire in 10 minutes.'
        },
    ]
    
    for template_data in templates:
        EmailTemplate.objects.get_or_create(
            template_type=template_data['template_type'],
            defaults=template_data
        )

def send_welcome_email(user, institution):
    """Send welcome email to new user"""
    context = {
        'user': user,
        'institution': institution
    }
    send_email_template('welcome', user, context)

# View functions
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Check if account is active
                if not user.is_active:
                    log_login_attempt(user, ip_address, user_agent, False, "Account inactive")
                    messages.error(request, 'Your account has been deactivated.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                # Check login attempts using utility function
                security_settings = get_security_settings(user)
                if check_login_attempts(user):
                    log_login_attempt(user, ip_address, user_agent, False, "Too many failed attempts")
                    messages.error(request, 'Too many failed login attempts. Please try again later.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                # Check if PIN verification is required
                try:
                    profile = UserProfile.objects.get(user=user)
                    if profile.pin:
                        # Store user ID in session for PIN verification
                        request.session['pending_user_id'] = user.id
                        request.session['pending_auth'] = True
                        log_login_attempt(user, ip_address, user_agent, True)
                        return redirect('accounts:verify_pin')
                except UserProfile.DoesNotExist:
                    pass
                
                # Login successful
                login(request, user)
                log_login_attempt(user, ip_address, user_agent, True)
                
                # Update last login IP
                profile = UserProfile.objects.get(user=user)
                profile.last_login_ip = ip_address
                profile.save()
                
                messages.success(request, 'Welcome back! You have been logged in successfully.')
                return redirect('dashboard:home')
            else:
                # Find user by email to log failed attempt
                try:
                    user = User.objects.get(email=email)
                    log_login_attempt(user, ip_address, user_agent, False, "Invalid password")
                except User.DoesNotExist:
                    log_login_attempt(None, ip_address, user_agent, False, "User not found")
                
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def verify_pin_view(request):
    if not request.session.get('pending_auth'):
        return redirect('accounts:login')
    
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('accounts:login')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        pin = request.POST.get('pin')
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if validate_pin(user, pin):
            login(request, user)
            log_login_attempt(user, ip_address, user_agent, True)
            
            # Clear session
            del request.session['pending_user_id']
            del request.session['pending_auth']
            
            messages.success(request, 'Welcome back! You have been logged in successfully.')
            return redirect('dashboard:home')
        else:
            log_login_attempt(user, ip_address, user_agent, False, "Invalid PIN")
            messages.error(request, 'Invalid PIN. Please try again.')
    
    return render(request, 'accounts/verify_pin.html', {'user': user})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = InstitutionRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            pin = form.cleaned_data['pin']
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name='',  # Will be updated later
                last_name=''
            )
            
            # Create institution
            institution = form.save(commit=False)
            institution.user = user
            institution.save()
            
           
            # Create security settings
            SecuritySettings.objects.create(user=user)
            
            # Create default email templates
            create_default_email_templates()
            
            # Send welcome email
            send_welcome_email(user, institution)
            
            # Log the user in
            login(request, user)
            
            messages.success(request, 'Your account has been created successfully! Welcome to Xpert Farmer IMS.')
            return redirect('accounts:registration_success')
    else:
        form = InstitutionRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def registration_success(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login') 
    
    return render(request, 'accounts/success.html')

def forgot_pin_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = ForgotPINForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            ip_address = get_client_ip(request)
            
            # Create OTP for PIN reset
            otp = create_otp_record(user, 'pin_reset', ip_address)
            
            # Send OTP email
            context = {'user': user, 'otp': otp}
            if send_email_template('pin_reset', user, context):
                request.session['reset_user_id'] = user.id
                messages.success(request, 'An OTP has been sent to your email address.')
                return redirect('accounts:reset_pin')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
    else:
        form = ForgotPINForm()
    
    return render(request, 'accounts/forgot_pin.html', {'form': form})

def reset_pin_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Invalid reset request.')
        return redirect('accounts:forgot_pin')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ResetPINForm(request.POST, user=user)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            new_pin = form.cleaned_data['new_pin']
            
            # Verify and mark OTP as used
            otp = OTP.objects.get(
                user=user,
                code=otp_code,
                otp_type='pin_reset',
                is_used=False
            )
            otp.is_used = True
            otp.save()
            
            # Update user PIN
            profile = UserProfile.objects.get(user=user)
            profile.pin = new_pin
            profile.save()
            
            # Clear session
            del request.session['reset_user_id']
            
            messages.success(request, 'Your PIN has been reset successfully. You can now login with your new PIN.')
            return redirect('accounts:login')
    else:
        form = ResetPINForm(user=user)
    
    return render(request, 'accounts/reset_pin.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    # Get login history
    login_history = LoginHistory.objects.filter(user=user).order_by('-login_time')[:10]
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'login_history': login_history,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def security_settings_view(request):
    user = request.user
    try:
        security_settings = SecuritySettings.objects.get(user=user)
    except SecuritySettings.DoesNotExist:
        security_settings = SecuritySettings.objects.create(user=user)
    
    if request.method == 'POST':
        # Remove 'user' parameter - SecuritySettingsForm doesn't accept it
        form = SecuritySettingsForm(request.POST, instance=security_settings)
        if form.is_valid():
            security_settings = form.save()
            messages.success(request, 'Your security settings have been updated.')
            return redirect('accounts:security_settings')
    else:
        # Remove 'user' parameter
        form = SecuritySettingsForm(instance=security_settings)
    
    context = {
        'form': form,
        'security_settings': security_settings,
    }
    return render(request, 'accounts/security_settings.html', context)

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/delete_account.html')

# API Views
@csrf_exempt
def api_check_email(request):
    """Check if email is available"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'available': not exists})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def api_send_verification_email(request):
    """Send email verification OTP"""
    user = request.user
    ip_address = get_client_ip(request)
    
    otp = create_otp_record(user, 'email_verification', ip_address)
    
    context = {'user': user, 'otp': otp}
    if send_email_template('verification', user, context):
        return JsonResponse({'success': True, 'message': 'Verification email sent successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'Failed to send verification email.'})

@login_required
def api_verify_email(request):
    """Verify email with OTP"""
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_code = data.get('otp')
        
        try:
            otp = OTP.objects.get(
                user=request.user,
                code=otp_code,
                otp_type='email_verification',
                is_used=False
            )
            
            from django.utils import timezone
            if not otp.is_used and timezone.now() < otp.expires_at:
                otp.is_used = True
                otp.save()
                
                profile = UserProfile.objects.get(user=request.user)
                profile.email_verified = True
                profile.save()
                
                return JsonResponse({'success': True, 'message': 'Email verified successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid or expired OTP.'})
        except OTP.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid OTP.'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

