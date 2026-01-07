from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid
from accounts.models import Institution

class Cluster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    creation_date = models.DateField()
    total_farmers = models.IntegerField(default=0)
    total_area = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    logo = models.ImageField(upload_to='clusters/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cluster"
        verbose_name_plural = "Clusters"
        ordering = ['-creation_date']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('dashboard:cluster_detail', kwargs={'cluster_id': self.id})
    
    def update_stats(self):
        """Update cluster statistics"""
        self.total_farmers = self.farmer_set.count()
        self.total_area = sum(farm.size for farm in self.farm_set.all() if farm.size)
        self.save()

class Farmer(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    years_farming = models.IntegerField(validators=[MinValueValidator(0)])
    country = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    residence_county = models.CharField(max_length=100, blank=True, null=True)
    residence_constituency = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='farmers/photos/', blank=True, null=True)
    clusters = models.ManyToManyField(Cluster, through='FarmerCluster', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Farmer"
        verbose_name_plural = "Farmers"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.farmer_id})"
    
    def get_absolute_url(self):
        return reverse('dashboard:farmer_detail', kwargs={'farmer_id': self.id})

class FarmerCluster(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Farmer Cluster Membership"
        verbose_name_plural = "Farmer Cluster Memberships"
        unique_together = ['farmer', 'cluster']

class Farm(models.Model):
    PRODUCTION_TYPES = [
        ('crop_corn', 'Crop (Corn)'),
        ('crop_wheat', 'Crop (Wheat)'),
        ('crop_vegetables', 'Crop (Vegetables)'),
        ('crop_fruits', 'Crop (Fruits)'),
        ('livestock_cattle', 'Livestock (Cattle)'),
        ('livestock_dairy', 'Livestock (Dairy)'),
        ('livestock_poultry', 'Livestock (Poultry)'),
        ('mixed', 'Mixed Farming'),
        ('horticulture', 'Horticulture'),
        ('aquaculture', 'Aquaculture'),
    ]
    
    OWNERSHIP_TYPES = [
        ('private', 'Private'),
        ('cooperative', 'Cooperative'),
        ('leased', 'Leased'),
        ('family', 'Family Owned'),
        ('communal', 'Communal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    ownership = models.CharField(max_length=20, choices=OWNERSHIP_TYPES)
    production_type = models.CharField(max_length=50, choices=PRODUCTION_TYPES)
    gps_coordinates = models.CharField(max_length=100, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    irrigation_type = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Farm"
        verbose_name_plural = "Farms"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.farmer.name}"
    
    def get_absolute_url(self):
        return reverse('dashboard:farm_detail', kwargs={'farm_id': self.id})

class ProductionData(models.Model):
    UNITS = [
        ('kg', 'Kilograms'),
        ('tons', 'Tons'),
        ('bushels', 'Bushels'),
        ('gallons', 'Gallons'),
        ('liters', 'Liters'),
        ('units', 'Units'),
        ('dozen', 'Dozen'),
        ('bags', 'Bags'),
        ('crates', 'Crates'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNITS)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    date_recorded = models.DateField()
    season = models.CharField(max_length=50, blank=True, null=True)
    quality_grade = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Production Data"
        verbose_name_plural = "Production Data"
        ordering = ['-date_recorded']
    
    def save(self, *args, **kwargs):
        self.total_revenue = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product_name} - {self.farm.name}"

class YieldData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    crop_livestock = models.CharField(max_length=255)
    area_count = models.DecimalField(max_digits=10, decimal_places=2)
    yield_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_yield = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    unit = models.CharField(max_length=20, default='tons')
    quality_grade = models.CharField(max_length=50)
    date_recorded = models.DateField()
    season = models.CharField(max_length=50, blank=True, null=True)
    rainfall_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    temperature_avg = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Yield Data"
        verbose_name_plural = "Yield Data"
        ordering = ['-date_recorded']
    
    def save(self, *args, **kwargs):
        self.total_yield = self.area_count * self.yield_per_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.crop_livestock} - {self.farm.name}"

class Labor(models.Model):
    CATEGORY_CHOICES = [
        ('permanent', 'Permanent'),
        ('casual', 'Casual'),
        ('seasonal', 'Seasonal'),
        ('contract', 'Contract'),
    ]
    
    ROLE_CHOICES = [
        ('farm_manager', 'Farm Manager'),
        ('harvester', 'Harvester'),
        ('operator', 'Equipment Operator'),
        ('packer', 'Packer'),
        ('supervisor', 'Supervisor'),
        ('feeder', 'Animal Feeder'),
        ('milker', 'Milker'),
        ('planter', 'Planter'),
        ('sprayer', 'Sprayer'),
        ('irrigator', 'Irrigator'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    employee_name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    hours_per_week = models.DecimalField(max_digits=4, decimal_places=1, default=40)
    status = models.CharField(max_length=20, default='active')
    date_hired = models.DateField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Labor"
        verbose_name_plural = "Labor Records"
        ordering = ['-date_hired']
    
    def weekly_cost(self):
        return self.hourly_rate * self.hours_per_week
    
    def monthly_cost(self):
        return self.weekly_cost() * 4
    
    def __str__(self):
        return f"{self.employee_name} - {self.role}"

class FarmInput(models.Model):
    CATEGORY_CHOICES = [
        ('seeds', 'Seeds'),
        ('fertilizer', 'Fertilizer'),
        ('pesticides', 'Pesticides'),
        ('feed', 'Animal Feed'),
        ('vaccinations', 'Vaccinations'),
        ('equipment', 'Equipment'),
        ('services', 'Services'),
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('water', 'Water'),
        ('electricity', 'Electricity'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    item_service = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Farm Input"
        verbose_name_plural = "Farm Inputs"
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item_service} - {self.farm.name}"

class Inventory(models.Model):
    CATEGORY_CHOICES = [
        ('machinery', 'Machinery'),
        ('infrastructure', 'Infrastructure'),
        ('supplies', 'Supplies'),
        ('tools', 'Tools'),
        ('vehicles', 'Vehicles'),
        ('buildings', 'Buildings'),
        ('equipment', 'Equipment'),
        ('storage', 'Storage'),
    ]
    
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Needs Repair'),
        ('retired', 'Retired'),
        ('sold', 'Sold'),
        ('lost', 'Lost'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    purchase_date = models.DateField()
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    last_maintenance = models.DateField(blank=True, null=True)
    next_maintenance = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='operational')
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.item_name} - {self.farm.name}"

class WaterInfrastructure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)
    setup_date = models.DateField()
    setup_cost = models.DecimalField(max_digits=15, decimal_places=2)
    consumption_rate = models.DecimalField(max_digits=10, decimal_places=2)
    consumption_unit = models.CharField(max_length=20, default='gal/day')
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='operational')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Water Infrastructure"
        verbose_name_plural = "Water Infrastructure"
        ordering = ['-setup_date']
    
    def __str__(self):
        return f"{self.source} - {self.farm.name}"

class UtilitiesPower(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    construction_date = models.DateField()
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    consumption_rate = models.DecimalField(max_digits=10, decimal_places=2)
    consumption_unit = models.CharField(max_length=20, default='kWh/month')
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Utilities & Power"
        verbose_name_plural = "Utilities & Power"
        ordering = ['-construction_date']
    
    def __str__(self):
        return f"{self.type} - {self.farm.name}"

class Report(models.Model):
    REPORT_TYPES = [
        ('operational', 'Operational Health'),
        ('profitability', 'Profitability'),
        ('productivity', 'Productivity & Efficiency'),
        ('sales', 'Sales & Market Insights'),
        ('resource', 'Cost & Resource Optimization'),
        ('trend', 'Trend & Forecast'),
        ('vine', 'Vine Reports'),
        ('yield', 'Yield Analysis'),
        ('labor', 'Labor Analysis'),
        ('inventory', 'Inventory Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_generated = models.DateTimeField(auto_now_add=True)
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    data_sources = models.JSONField(default=dict)
    insights = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True, null=True)
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-date_generated']
    
    def __str__(self):
        return f"{self.title} - {self.report_type}"

class DashboardSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_date_range = models.CharField(max_length=20, default='month')
    show_charts = models.BooleanField(default=True)
    show_notifications = models.BooleanField(default=True)
    items_per_page = models.IntegerField(default=25)
    theme = models.CharField(max_length=20, default='light')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Setting"
        verbose_name_plural = "Dashboard Settings"
    
    def __str__(self):
        return f"Settings - {self.user.username}"