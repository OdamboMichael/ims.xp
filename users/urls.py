from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('create/', views.user_create, name='create'),
    path('<int:user_id>/', views.user_manage, name='manage'),
    path('<int:user_id>/delete/', views.user_delete, name='delete'),
    path('bulk-action/', views.user_bulk_action, name='bulk_action'),
    path('api/<int:user_id>/activity/', views.user_activity_log, name='user_activity'),
    path('api/session/<int:session_id>/terminate/', views.terminate_session, name='terminate_session'),
    path('api/<int:user_id>/terminate-all/', views.terminate_all_sessions, name='terminate_all'),
]