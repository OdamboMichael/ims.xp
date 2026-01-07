from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Cluster, Farmer, Farm, ProductionData, YieldData,
    Labor, FarmInput, Inventory, WaterInfrastructure, 
    UtilitiesPower, Report
)

@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'total_farmers', 'total_area', 'creation_date', 'institution', 'is_active')
    list_filter = ('is_active', 'creation_date', 'institution')
    search_fields = ('name', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('institution', 'name', 'description', 'location', 'logo')
        }),
        ('Statistics', {
            'fields': ('total_farmers', 'total_area', 'creation_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer_id', 'age', 'gender', 'country', 'years_farming', 'is_active')
    list_filter = ('gender', 'country', 'is_active', 'created_at')
    search_fields = ('name', 'farmer_id', 'email', 'phone', 'national_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('farmer_id', 'name', 'email', 'phone', 'national_id', 'age', 'gender', 'photo')
        }),
        ('Farming Experience', {
            'fields': ('years_farming',)
        }),
        ('Location', {
            'fields': ('country', 'county', 'constituency', 'ward', 'residence_county', 'residence_constituency')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 30

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'cluster', 'production_type', 'size', 'county', 'is_active')
    list_filter = ('production_type', 'ownership', 'country', 'is_active')
    search_fields = ('name', 'farmer__name', 'cluster__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'farmer', 'cluster', 'production_type', 'ownership')
        }),
        ('Location', {
            'fields': ('country', 'county', 'constituency', 'ward', 'gps_coordinates')
        }),
        ('Farm Details', {
            'fields': ('size', 'soil_type', 'irrigation_type')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 25

@admin.register(ProductionData)
class ProductionDataAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'farm', 'quantity', 'unit', 'price_per_unit', 'total_revenue', 'date_recorded')
    list_filter = ('product_type', 'date_recorded', 'unit')
    search_fields = ('product_name', 'farm__name')
    readonly_fields = ('total_revenue', 'created_at')
    fieldsets = (
        ('Product Information', {
            'fields': ('farm', 'product_name', 'product_type', 'quantity', 'unit')
        }),
        ('Pricing', {
            'fields': ('price_per_unit', 'total_revenue')
        }),
        ('Additional Information', {
            'fields': ('date_recorded', 'season', 'quality_grade', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

@admin.register(YieldData)
class YieldDataAdmin(admin.ModelAdmin):
    list_display = ('crop_livestock', 'farm', 'area_count', 'yield_per_unit', 'total_yield', 'quality_grade', 'date_recorded')
    list_filter = ('quality_grade', 'date_recorded', 'season')
    search_fields = ('crop_livestock', 'farm__name')
    readonly_fields = ('total_yield',)
    fieldsets = (
        ('Yield Information', {
            'fields': ('farm', 'crop_livestock', 'area_count', 'yield_per_unit', 'unit', 'total_yield')
        }),
        ('Quality & Environment', {
            'fields': ('quality_grade', 'rainfall_mm', 'temperature_avg')
        }),
        ('Timing', {
            'fields': ('date_recorded', 'season')
        }),
    )
    list_per_page = 20

@admin.register(Labor)
class LaborAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'farm', 'category', 'role', 'hourly_rate', 'status', 'date_hired')
    list_filter = ('category', 'role', 'status', 'date_hired')
    search_fields = ('employee_name', 'farm__name')
    readonly_fields = ('weekly_cost',)
    fieldsets = (
        ('Employee Information', {
            'fields': ('farm', 'employee_name', 'category', 'role')
        }),
        ('Employment Details', {
            'fields': ('hourly_rate', 'hours_per_week', 'date_hired', 'phone', 'email')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    list_per_page = 25

@admin.register(FarmInput)
class FarmInputAdmin(admin.ModelAdmin):
    list_display = ('item_service', 'farm', 'category', 'quantity', 'unit', 'unit_cost', 'total_cost', 'date')
    list_filter = ('category', 'date')
    search_fields = ('item_service', 'farm__name', 'supplier')
    readonly_fields = ('total_cost',)
    fieldsets = (
        ('Input Information', {
            'fields': ('farm', 'date', 'category', 'item_service')
        }),
        ('Quantity & Cost', {
            'fields': ('quantity', 'unit', 'unit_cost', 'total_cost')
        }),
        ('Supplier Information', {
            'fields': ('supplier', 'receipt_number', 'notes')
        }),
    )
    list_per_page = 20

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'farm', 'category', 'purchase_date', 'cost', 'status', 'last_maintenance')
    list_filter = ('category', 'status', 'purchase_date')
    search_fields = ('item_name', 'farm__name', 'description')
    fieldsets = (
        ('Item Information', {
            'fields': ('farm', 'category', 'item_name', 'description')
        }),
        ('Purchase & Value', {
            'fields': ('purchase_date', 'cost', 'current_value', 'depreciation_rate')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance', 'next_maintenance', 'status')
        }),
    )
    list_per_page = 20

@admin.register(WaterInfrastructure)
class WaterInfrastructureAdmin(admin.ModelAdmin):
    list_display = ('source', 'farm', 'setup_date', 'setup_cost', 'consumption_rate', 'monthly_cost', 'status')
    list_filter = ('status', 'setup_date')
    search_fields = ('source', 'farm__name')
    list_per_page = 15

@admin.register(UtilitiesPower)
class UtilitiesPowerAdmin(admin.ModelAdmin):
    list_display = ('type', 'farm', 'construction_date', 'cost', 'consumption_rate', 'monthly_cost')
    list_filter = ('type', 'construction_date')
    search_fields = ('type', 'farm__name')
    list_per_page = 15

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'institution', 'generated_by', 'date_generated', 'date_range_start', 'date_range_end')
    list_filter = ('report_type', 'date_generated', 'institution')
    search_fields = ('title', 'institution__name')
    readonly_fields = ('date_generated', 'generated_by')
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'report_type', 'institution')
        }),
        ('Date Range', {
            'fields': ('date_range_start', 'date_range_end')
        }),
        ('Content', {
            'fields': ('data_sources', 'insights', 'recommendations', 'file_path')
        }),
        ('Generation Info', {
            'fields': ('generated_by', 'date_generated'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 15
    
    def save_model(self, request, obj, form, change):
        if not obj.generated_by_id:
            obj.generated_by = request.user
        super().save_model(request, obj, form, change)

# Custom admin site title and header
admin.site.site_header = "Xpert Farmer IMS Administration"
admin.site.site_title = "Xpert Farmer IMS Admin"
admin.site.index_title = "Dashboard Administration"