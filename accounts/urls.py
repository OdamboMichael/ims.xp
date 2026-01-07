from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('verify-pin/', views.verify_pin_view, name='verify_pin'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.register_view, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    
    # Password/PIN Management
    path('forgot-pin/', views.forgot_pin_view, name='forgot_pin'),
    path('reset-pin/', views.reset_pin_view, name='reset_pin'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('security-settings/', views.security_settings_view, name='security_settings'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # API Endpoints
    path('api/check-email/', views.api_check_email, name='api_check_email'),
    path('api/send-verification-email/', views.api_send_verification_email, name='api_send_verification_email'),
    path('api/verify-email/', views.api_verify_email, name='api_verify_email'),
]