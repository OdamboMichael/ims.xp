from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, UserActivity

class UserCreateForm(UserCreationForm):
    """Form for creating new users"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    job_title = forms.CharField(max_length=100, required=False)
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES, required=True)
    send_welcome_email = forms.BooleanField(required=False, initial=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.job_title = self.cleaned_data.get('job_title', '')
            profile.status = 'active' if self.cleaned_data.get('send_welcome_email') else 'pending'
            profile.update_permissions_from_role()
            profile.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='create',
                description=f"User account created"
            )
        
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing users"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ('role', 'status', 'phone_number', 'job_title', 'profile_picture',
                 'can_manage_farms', 'can_manage_users', 'can_generate_reports',
                 'can_export_data', 'can_access_api', 'can_manage_settings')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make role field change trigger permission updates in view


class PasswordResetForm(forms.Form):
    """Form for resetting user password"""
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    force_change = forms.BooleanField(required=False, initial=True)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data


class UserSearchForm(forms.Form):
    """Form for searching/filtering users"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search users...'}))
    role = forms.ChoiceField(choices=[('', 'All Roles')] + UserProfile.USER_ROLES, required=False)
    status = forms.ChoiceField(choices=[('', 'All Status')] + UserProfile.STATUS_CHOICES, required=False)