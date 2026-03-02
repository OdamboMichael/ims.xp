from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
import json

from .models import UserProfile, UserActivity, UserSession
from .forms import UserCreateForm, UserEditForm, UserProfileForm, PasswordResetForm, UserSearchForm
from dashboard.models import Institution

def is_admin(user):
    """Check if user has admin role"""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 'admin' or user.is_superuser
    except:
        return user.is_superuser

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users in the organization"""
    # Get user's institution
    try:
        institution = Institution.objects.get(user=request.user)
        users = User.objects.filter(profile__institution=institution)
    except Institution.DoesNotExist:
        # Superuser can see all users
        if request.user.is_superuser:
            users = User.objects.all()
        else:
            users = User.objects.filter(profile__institution__isnull=True)
    
    # Apply filters
    form = UserSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        role = form.cleaned_data.get('role')
        status = form.cleaned_data.get('status')
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            users = users.filter(profile__role=role)
        
        if status:
            users = users.filter(profile__status=status)
    
    # Statistics
    total_users = users.count()
    active_users = users.filter(profile__status='active').count()
    admin_count = users.filter(profile__role='admin').count()
    manager_count = users.filter(profile__role='manager').count()
    analyst_count = users.filter(profile__role='analyst').count()
    viewer_count = users.filter(profile__role='viewer').count()
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'manager_count': manager_count,
        'analyst_count': analyst_count,
        'viewer_count': viewer_count,
        'role_stats': json.dumps({
            'labels': ['Admin', 'Manager', 'Analyst', 'Viewer'],
            'data': [admin_count, manager_count, analyst_count, viewer_count]
        }),
    }
    
    return render(request, 'users/list.html', context)

@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Assign to institution
            try:
                institution = Institution.objects.get(user=request.user)
                user.profile.institution = institution
                user.profile.save()
            except Institution.DoesNotExist:
                pass
            
            # Set created_by
            user.profile.created_by = request.user
            user.profile.save()
            
            messages.success(request, f'User {user.get_full_name()} created successfully!')
            
            # Send welcome email if requested
            if form.cleaned_data.get('send_welcome_email'):
                # Implement email sending here
                pass
            
            return redirect('users:manage', user_id=user.id)
    else:
        form = UserCreateForm()
    
    context = {
        'form': form,
    }
    return render(request, 'users/create.html', context)

@login_required
@user_passes_test(is_admin)
def user_manage(request, user_id):
    """Manage a specific user"""
    user = get_object_or_404(User, id=user_id)
    
    # Check permission to manage this user
    try:
        institution = Institution.objects.get(user=request.user)
        if not request.user.is_superuser and user.profile.institution != institution:
            messages.error(request, "You don't have permission to manage this user.")
            return redirect('users:list')
    except Institution.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to manage users.")
            return redirect('users:list')
    
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            user_form = UserEditForm(request.POST, instance=user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user.profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile = profile_form.save(commit=False)
                
                # Update permissions based on role if role changed
                if 'role' in profile_form.changed_data:
                    profile.update_permissions_from_role()
                
                profile.save()
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='update',
                    description="Profile updated by admin"
                )
                
                messages.success(request, f'User {user.get_full_name()} updated successfully!')
                return redirect('users:manage', user_id=user.id)
        
        elif 'reset_password' in request.POST:
            password_form = PasswordResetForm(request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                
                if password_form.cleaned_data['force_change']:
                    # Set password change required flag
                    pass
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='update',
                    description="Password reset by admin"
                )
                
                messages.success(request, f'Password reset for {user.get_full_name()} successfully!')
                return redirect('users:manage', user_id=user.id)
    
    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)
    
    # Get user activity
    activities = UserActivity.objects.filter(user=user)[:10]
    
    # Get active sessions
    sessions = UserSession.objects.filter(user=user)[:5]
    
    context = {
        'manage_user': user,
        'user_form': user_form,
        'profile_form': profile_form,
        'activities': activities,
        'sessions': sessions,
    }
    
    return render(request, 'users/manage.html', context)

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    """Delete a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Don't allow deleting yourself
        if user == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect('users:list')
        
        user.delete()
        messages.success(request, f'User deleted successfully!')
    
    return redirect('users:list')

@login_required
@user_passes_test(is_admin)
def user_bulk_action(request):
    """Handle bulk actions on users"""
    if request.method == 'POST':
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.error(request, "No users selected.")
            return redirect('users:list')
        
        users = User.objects.filter(id__in=user_ids)
        
        if action == 'activate':
            users.update(profile__status='active')
            messages.success(request, f"{len(user_ids)} users activated.")
        elif action == 'deactivate':
            users.update(profile__status='inactive')
            messages.success(request, f"{len(user_ids)} users deactivated.")
        elif action == 'delete':
            # Don't allow deleting self
            users = users.exclude(id=request.user.id)
            count = users.count()
            users.delete()
            messages.success(request, f"{count} users deleted.")
        
        # Log bulk activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='update',
            description=f"Bulk action '{action}' on {len(user_ids)} users"
        )
    
    return redirect('users:list')

@login_required
def user_activity_log(request, user_id):
    """Get user activity log (AJAX)"""
    user = get_object_or_404(User, id=user_id)
    activities = UserActivity.objects.filter(user=user)[:20]
    
    data = [{
        'type': a.activity_type,
        'description': a.description,
        'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M'),
        'ip': a.ip_address,
    } for a in activities]
    
    return JsonResponse({'activities': data})

@login_required
@user_passes_test(is_admin)
def terminate_session(request, session_id):
    """Terminate a user session"""
    if request.method == 'POST':
        session = get_object_or_404(UserSession, id=session_id)
        session.delete()
        
        # Log activity
        UserActivity.objects.create(
            user=session.user,
            activity_type='logout',
            description="Session terminated by admin"
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_admin)
def terminate_all_sessions(request, user_id):
    """Terminate all sessions for a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        count = UserSession.objects.filter(user=user).delete()[0]
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='logout',
            description=f"{count} sessions terminated by admin"
        )
        
        return JsonResponse({'success': True, 'count': count})
    
    return JsonResponse({'success': False}, status=400)