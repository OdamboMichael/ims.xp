from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Institution, UserProfile, OTP, SecuritySettings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field

class InstitutionRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'class': 'form-control'
        }),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        })
    )
    pin = forms.CharField(
        max_length=6,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a 4-6 digit PIN',
            'class': 'form-control',
            'maxlength': '6'
        }),
        validators=[
            RegexValidator(
                regex='^[0-9]{4,6}$',
                message='PIN must be 4-6 digits'
            )
        ]
    )
    confirm_pin = forms.CharField(
        max_length=6,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your PIN',
            'class': 'form-control',
            'maxlength': '6'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions'}
    )

    class Meta:
        model = Institution
        fields = [
            'name', 'institution_type', 'registration_number', 
            'country', 'constituency', 'ward', 'street', 'email',
            'clusters_count', 'phone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name of institution'}),
            'street': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Street / Road'}),
            'registration_number': forms.TextInput(attrs={'placeholder': 'Optional'}),
            'clusters_count': forms.NumberInput(attrs={'min': 1, 'max': 100}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-4">Create an Institutional Account</h4>'),
            
            Row(
                Column('institution_type', css_class='col-md-6'),
                Column('name', css_class='col-md-6'),
            ),
            Row(
                Column('registration_number', css_class='col-md-6'),
                Column('clusters_count', css_class='col-md-6'),
            ),
            Row(
                Column('country', css_class='col-md-6'),
                Column('constituency', css_class='col-md-6'),
            ),
            Row(
                Column('ward', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            'street',
            HTML('<hr class="my-4">'),
            HTML('<h5 class="mb-3">Account Setup</h5>'),
            'email',
            Row(
                Column('password', css_class='col-md-6'),
                Column('confirm_password', css_class='col-md-6'),
            ),
            Row(
                Column('pin', css_class='col-md-6'),
                Column('confirm_pin', css_class='col-md-6'),
            ),
            Div(
                Field('agree_terms', css_class='form-check-input'),
                HTML('<label class="form-check-label" for="id_agree_terms">'
                     'I agree to the <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">Terms and Conditions</a>'
                     '</label>'),
                css_class='form-check mb-4'
            ),
            Submit('submit', 'Create Account', css_class='btn btn-primary btn-lg w-100')
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Institution.objects.filter(email=email).exists():
            raise forms.ValidationError('An institution with this email already exists')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        pin = cleaned_data.get('pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        email = cleaned_data.get('email')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        
        if pin and confirm_pin and pin != confirm_pin:
            self.add_error('confirm_pin', 'PINs do not match')
        
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', 'A user with this email already exists')
        
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            'username',
            'password',
            Div(
                HTML('<a href="{% url "accounts:forgot_pin" %}" class="text-decoration-none">Forgot Pin?</a>'),
                css_class='d-flex justify-content-end mb-3'
            ),
            Submit('submit', 'Login', css_class='btn btn-primary btn-lg w-100')
        )

class ForgotPINForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'email',
            Submit('submit', 'Request OTP', css_class='btn btn-primary w-100 mt-3')
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address')
        return email

class ResetPINForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the OTP sent to your email',
            'class': 'form-control'
        })
    )
    new_pin = forms.CharField(
        max_length=6,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your new PIN',
            'class': 'form-control',
            'maxlength': '6'
        }),
        validators=[
            RegexValidator(
                regex='^[0-9]{4,6}$',
                message='PIN must be 4-6 digits'
            )
        ]
    )
    confirm_pin = forms.CharField(
        max_length=6,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your new PIN',
            'class': 'form-control',
            'maxlength': '6'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'otp',
            'new_pin',
            'confirm_pin',
            Submit('submit', 'Reset Pin', css_class='btn btn-primary w-100 mt-3')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        otp = cleaned_data.get('otp')
        
        if new_pin and confirm_pin and new_pin != confirm_pin:
            self.add_error('confirm_pin', 'PINs do not match')
        
        if otp and self.user:
            try:
                otp_obj = OTP.objects.get(
                    user=self.user,
                    code=otp,
                    otp_type='pin_reset',
                    is_used=False
                )
                if not otp_obj.is_valid():
                    self.add_error('otp', 'Invalid or expired OTP')
            except OTP.DoesNotExist:
                self.add_error('otp', 'Invalid OTP')
        
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'email',
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'profile_picture', 'job_title', 'department']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'phone',
            'profile_picture',
            'job_title',
            'department',
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )

class SecuritySettingsForm(forms.ModelForm):
    class Meta:
        model = SecuritySettings
        fields = [
            'two_factor_enabled', 
            'login_notifications', 
            'session_timeout', 
            'max_login_attempts'
        ]
        labels = {
            'two_factor_enabled': 'Enable Two-Factor Authentication',
            'login_notifications': 'Send Login Notifications',
            'session_timeout': 'Session Timeout (minutes)',
            'max_login_attempts': 'Maximum Login Attempts'
        }
        help_texts = {
            'two_factor_enabled': 'Require OTP for login in addition to password',
            'login_notifications': 'Receive email notifications for new logins',
            'session_timeout': 'Time before automatic logout (5-1440 minutes)',
            'max_login_attempts': 'Maximum failed login attempts before lockout'
        }
        widgets = {
            'session_timeout': forms.NumberInput(attrs={
                'min': 5, 
                'max': 1440,
                'class': 'form-control'
            }),
            'max_login_attempts': forms.NumberInput(attrs={
                'min': 1, 
                'max': 10,
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-4">Security Settings</h4>'),
            Div(
                Field('two_factor_enabled', css_class='form-check-input'),
                HTML('<label class="form-check-label" for="id_two_factor_enabled">Enable Two-Factor Authentication</label>'),
                css_class='form-check mb-3'
            ),
            Div(
                Field('login_notifications', css_class='form-check-input'),
                HTML('<label class="form-check-label" for="id_login_notifications">Send Login Notifications</label>'),
                css_class='form-check mb-3'
            ),
            'session_timeout',
            'max_login_attempts',
            Submit('submit', 'Save Security Settings', css_class='btn btn-primary mt-3')
        )
    
    def clean_session_timeout(self):
        session_timeout = self.cleaned_data.get('session_timeout')
        if session_timeout < 5 or session_timeout > 1440:
            raise forms.ValidationError("Session timeout must be between 5 and 1440 minutes.")
        return session_timeout
    
    def clean_max_login_attempts(self):
        max_login_attempts = self.cleaned_data.get('max_login_attempts')
        if max_login_attempts < 1 or max_login_attempts > 10:
            raise forms.ValidationError("Maximum login attempts must be between 1 and 10.")
        return max_login_attempts
    
    def clean(self):
        cleaned_data = super().clean()
        two_factor_enabled = cleaned_data.get('two_factor_enabled')
        session_timeout = cleaned_data.get('session_timeout')
        
        # If two-factor is enabled, ensure session timeout is reasonable
        if two_factor_enabled and session_timeout < 15:
            self.add_error('session_timeout', 
                         'When two-factor authentication is enabled, session timeout should be at least 15 minutes for security.')
        
        return cleaned_data