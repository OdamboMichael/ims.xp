from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home
    path('', views.home, name='home'),
    
    # Clusters Management
    path('clusters/', views.clusters_list, name='clusters_list'),
    path('clusters/create/', views.cluster_create, name='cluster_create'),
    path('clusters/<uuid:cluster_id>/', views.cluster_detail, name='cluster_detail'),
    path('clusters/<uuid:cluster_id>/edit/', views.cluster_edit, name='cluster_edit'),
    path('clusters/<uuid:cluster_id>/delete/', views.cluster_delete, name='cluster_delete'),
    path('clusters/<uuid:cluster_id>/add-farmer/', views.cluster_add_farmer, name='cluster_add_farmer'),
    path('clusters/<uuid:cluster_id>/remove-farmer/<uuid:farmer_id>/', views.cluster_remove_farmer, name='cluster_remove_farmer'),
    
    # Farms Management
    path('farms/', views.farms_list, name='farms_list'),
    path('farms/create/', views.farm_create, name='farm_create'),
    path('farms/<uuid:farm_id>/', views.farm_detail, name='farm_detail'),
    path('farms/<uuid:farm_id>/edit/', views.farm_edit, name='farm_edit'),
    path('farms/<uuid:farm_id>/delete/', views.farm_delete, name='farm_delete'),
    
    # Farmers Management
    path('farmers/', views.farmers_list, name='farmers_list'),
    path('farmers/create/', views.farmer_create, name='farmer_create'),
    path('farmers/<uuid:farmer_id>/', views.farmer_detail, name='farmer_detail'),
    path('farmers/<uuid:farmer_id>/edit/', views.farmer_edit, name='farmer_edit'),
    path('farmers/<uuid:farmer_id>/delete/', views.farmer_delete, name='farmer_delete'),
    
    # Production Data
    path('production/overview/', views.production_overview, name='overview'),
    path('production/sales/', views.sales_revenue, name='sales_revenue'),
    path('production/sales/create/', views.sales_create, name='sales_create'),
    path('production/yield/', views.yield_data, name='yield_data'),
    path('production/yield/create/', views.yield_create, name='yield_create'),
    path('production/labor/', views.labor_management, name='labor'),
    path('production/labor/create/', views.labor_create, name='labor_create'),
    path('production/inputs/', views.farm_inputs, name='inputs'),
    path('production/inputs/create/', views.inputs_create, name='inputs_create'),
    path('production/inventory/', views.inventory_management, name='inventory'),
    path('production/inventory/create/', views.inventory_create, name='inventory_create'),
    
    # Reports
    path('reports/', views.reports_main, name='reports_main'),
    path('reports/generate/', views.report_generate, name='report_generate'),
    path('reports/<uuid:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<uuid:report_id>/download/', views.report_download, name='report_download'),
    path('reports/<uuid:report_id>/delete/', views.report_delete, name='report_delete'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('settings/profile/', views.profile_settings, name='profile_settings'),
    path('settings/display/', views.display_settings, name='display_settings'),
    
    # API Endpoints
    path('api/cluster-stats/', views.api_cluster_stats, name='api_cluster_stats'),
    path('api/farmer-stats/', views.api_farmer_stats, name='api_farmer_stats'),
    path('api/production-chart/', views.api_production_chart, name='api_production_chart'),
    path('api/yield-chart/', views.api_yield_chart, name='api_yield_chart'),
    path('api/revenue-chart/', views.api_revenue_chart, name='api_revenue_chart'),
    
    # Export Data
    path('export/farms/', views.export_farms, name='export_farms'),
    path('export/farmers/', views.export_farmers, name='export_farmers'),
    path('export/production/', views.export_production, name='export_production'),
    path('export/yield/', views.export_yield, name='export_yield'),
    path('export/report/<uuid:report_id>/', views.export_report, name='export_report'),
    
    # Utility Pages
    path('search/', views.global_search, name='global_search'),
    path('notifications/', views.notifications, name='notifications'),
    path('help/', views.help_center, name='help_center'),

    path('users/', views.user_list, name='user_list'),

]
