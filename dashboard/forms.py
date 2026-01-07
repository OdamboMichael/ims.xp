from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field
from crispy_forms.bootstrap import Accordion, AccordionGroup
from .models import (
    Cluster, Farmer, Farm, ProductionData, YieldData,
    Labor, FarmInput, Inventory, WaterInfrastructure,
    UtilitiesPower, Report
)

class ClusterForm(forms.ModelForm):
    class Meta:
        model = Cluster
        fields = ['name', 'description', 'location', 'creation_date', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the cluster objectives and activities...'}),
            'creation_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-8'),
                Column('creation_date', css_class='col-md-4'),
            ),
            'location',
            'description',
            Div(
                HTML('<label class="form-label">Cluster Logo</label>'),
                'logo',
                css_class='mb-3'
            ),
            Div(
                Submit('submit', 'Save Cluster', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:clusters_list" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end'
            )
        )

class FarmerForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = [
            'farmer_id', 'name', 'email', 'phone', 'national_id',
            'age', 'gender', 'years_farming', 'country', 'county',
            'constituency', 'ward', 'residence_county', 'residence_constituency', 'photo'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'min': 18, 'max': 100}),
            'years_farming': forms.NumberInput(attrs={'min': 0}),
            'phone': forms.TextInput(attrs={'placeholder': '+254 XXX XXX XXX'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(
                    'Personal Information',
                    Row(
                        Column('farmer_id', css_class='col-md-6'),
                        Column('name', css_class='col-md-6'),
                    ),
                    Row(
                        Column('email', css_class='col-md-6'),
                        Column('phone', css_class='col-md-6'),
                    ),
                    Row(
                        Column('national_id', css_class='col-md-6'),
                        Column('age', css_class='col-md-3'),
                        Column('gender', css_class='col-md-3'),
                    ),
                    Row(
                        Column('years_farming', css_class='col-md-6'),
                        Column('photo', css_class='col-md-6'),
                    ),
                    active=True
                ),
                AccordionGroup(
                    'Location Details',
                    Row(
                        Column('country', css_class='col-md-6'),
                        Column('county', css_class='col-md-6'),
                    ),
                    Row(
                        Column('constituency', css_class='col-md-6'),
                        Column('ward', css_class='col-md-6'),
                    ),
                    Row(
                        Column('residence_county', css_class='col-md-6'),
                        Column('residence_constituency', css_class='col-md-6'),
                    )
                )
            ),
            Div(
                Submit('submit', 'Save Farmer', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:farmers_list" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end mt-4'
            )
        )

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = [
            'name', 'farmer', 'cluster', 'country', 'county', 'constituency', 'ward',
            'size', 'ownership', 'production_type', 'gps_coordinates',
            'soil_type', 'irrigation_type'
        ]
        widgets = {
            'size': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'gps_coordinates': forms.TextInput(attrs={'placeholder': 'e.g., -1.2921, 36.8219'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(
                    'Farm Information',
                    Row(
                        Column('name', css_class='col-md-8'),
                        Column('size', css_class='col-md-4'),
                    ),
                    Row(
                        Column('farmer', css_class='col-md-6'),
                        Column('cluster', css_class='col-md-6'),
                    ),
                    Row(
                        Column('ownership', css_class='col-md-6'),
                        Column('production_type', css_class='col-md-6'),
                    ),
                    active=True
                ),
                AccordionGroup(
                    'Location Details',
                    Row(
                        Column('country', css_class='col-md-6'),
                        Column('county', css_class='col-md-6'),
                    ),
                    Row(
                        Column('constituency', css_class='col-md-6'),
                        Column('ward', css_class='col-md-6'),
                    ),
                    'gps_coordinates'
                ),
                AccordionGroup(
                    'Farm Characteristics',
                    Row(
                        Column('soil_type', css_class='col-md-6'),
                        Column('irrigation_type', css_class='col-md-6'),
                    )
                )
            ),
            Div(
                Submit('submit', 'Save Farm', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:farms_list" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end mt-4'
            )
        )

class ProductionDataForm(forms.ModelForm):
    class Meta:
        model = ProductionData
        fields = [
            'farm', 'product_name', 'product_type', 'quantity', 'unit',
            'price_per_unit', 'date_recorded', 'season', 'quality_grade', 'notes'
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'price_per_unit': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'date_recorded': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes about this production...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('farm', css_class='col-md-6'),
                Column('date_recorded', css_class='col-md-6'),
            ),
            Row(
                Column('product_name', css_class='col-md-6'),
                Column('product_type', css_class='col-md-6'),
            ),
            Row(
                Column('quantity', css_class='col-md-4'),
                Column('unit', css_class='col-md-4'),
                Column('price_per_unit', css_class='col-md-4'),
            ),
            Row(
                Column('season', css_class='col-md-6'),
                Column('quality_grade', css_class='col-md-6'),
            ),
            'notes',
            Div(
                Submit('submit', 'Save Production Data', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:production_overview" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end'
            )
        )

class YieldDataForm(forms.ModelForm):
    class Meta:
        model = YieldData
        fields = [
            'farm', 'crop_livestock', 'area_count', 'yield_per_unit', 'unit',
            'quality_grade', 'date_recorded', 'season', 'rainfall_mm', 'temperature_avg'
        ]
        widgets = {
            'area_count': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'yield_per_unit': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'date_recorded': forms.DateInput(attrs={'type': 'date'}),
            'rainfall_mm': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'temperature_avg': forms.NumberInput(attrs={'step': '0.1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('farm', css_class='col-md-6'),
                Column('date_recorded', css_class='col-md-6'),
            ),
            Row(
                Column('crop_livestock', css_class='col-md-6'),
                Column('season', css_class='col-md-6'),
            ),
            Row(
                Column('area_count', css_class='col-md-4'),
                Column('yield_per_unit', css_class='col-md-4'),
                Column('unit', css_class='col-md-4'),
            ),
            Row(
                Column('quality_grade', css_class='col-md-6'),
                Column('rainfall_mm', css_class='col-md-3'),
                Column('temperature_avg', css_class='col-md-3'),
            ),
            Div(
                Submit('submit', 'Save Yield Data', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:yield_data" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end'
            )
        )

class LaborForm(forms.ModelForm):
    class Meta:
        model = Labor
        fields = [
            'farm', 'employee_name', 'category', 'role', 'hourly_rate',
            'hours_per_week', 'status', 'date_hired', 'phone', 'email'
        ]
        widgets = {
            'hourly_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'hours_per_week': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '168'}),
            'date_hired': forms.DateInput(attrs={'type': 'date'}),
            'email': forms.EmailInput(attrs={'placeholder': 'employee@example.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('farm', css_class='col-md-6'),
                Column('date_hired', css_class='col-md-6'),
            ),
            Row(
                Column('employee_name', css_class='col-md-6'),
                Column('category', css_class='col-md-3'),
                Column('role', css_class='col-md-3'),
            ),
            Row(
                Column('hourly_rate', css_class='col-md-4'),
                Column('hours_per_week', css_class='col-md-4'),
                Column('status', css_class='col-md-4'),
            ),
            Row(
                Column('phone', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            Div(
                Submit('submit', 'Save Labor Record', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:labor" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end'
            )
        )

class FarmInputForm(forms.ModelForm):
    class Meta:
        model = FarmInput
        fields = [
            'farm', 'date', 'category', 'item_service', 'quantity', 'unit',
            'unit_cost', 'supplier', 'receipt_number', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes about this input...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('farm', css_class='col-md-6'),
                Column('date', css_class='col-md-6'),
            ),
            Row(
                Column('category', css_class='col-md-6'),
                Column('item_service', css_class='col-md-6'),
            ),
            Row(
                Column('quantity', css_class='col-md-4'),
                Column('unit', css_class='col-md-4'),
                Column('unit_cost', css_class='col-md-4'),
            ),
            Row(
                Column('supplier', css_class='col-md-6'),
                Column('receipt_number', css_class='col-md-6'),
            ),
            'notes',
            Div(
                Submit('submit', 'Save Input Record', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:inputs" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end'
            )
        )

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'farm', 'category', 'item_name', 'description', 'purchase_date',
            'cost', 'current_value', 'last_maintenance', 'next_maintenance',
            'status', 'depreciation_rate'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'current_value': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'depreciation_rate': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '100'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the inventory item...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('farm', css_class='col-md-6'),
                Column('category', css_class='col-md-6'),
            ),
            Row(
                Column('item_name', css_class='col-md-6'),
                Column('purchase_date', css_class='col-md-6'),
            ),
            Row(
                Column('cost', css_class='col-md-4'),
                Column('current_value', css_class='col-md-4'),
                Column('depreciation_rate', css_class='col-md-4'),
            ),
            Row(
                Column('last_maintenance', css_class='col-md-6'),
                Column('next_maintenance', css_class='col-md-6'),
            ),
            Row(
                Column('status', css_class='col-md-6'),
            ),
            'description',
            Div(
                Submit('submit', 'Save Inventory Item', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url "dashboard:inventory" %}" class="btn btn-secondary">Cancel</a>'),
                css_class='d-flex justify-content-end'
            )
        )

class WaterInfrastructureForm(forms.ModelForm):
    class Meta:
        model = WaterInfrastructure
        fields = ['farm', 'source', 'setup_date', 'setup_cost', 'consumption_rate', 'consumption_unit', 'monthly_cost', 'status']
        widgets = {
            'setup_date': forms.DateInput(attrs={'type': 'date'}),
            'setup_cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'consumption_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'monthly_cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

class UtilitiesPowerForm(forms.ModelForm):
    class Meta:
        model = UtilitiesPower
        fields = ['farm', 'type', 'construction_date', 'cost', 'consumption_rate', 'consumption_unit', 'monthly_cost']
        widgets = {
            'construction_date': forms.DateInput(attrs={'type': 'date'}),
            'cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'consumption_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'monthly_cost': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

class ReportFilterForm(forms.Form):
    DATE_RANGE_CHOICES = [
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('quarter', 'This Quarter'),
        ('year', 'This Year'),
        ('custom', 'Custom Range'),
    ]
    
    report_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Report.REPORT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_range = forms.ChoiceField(
        choices=DATE_RANGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    farmer = forms.ModelChoiceField(
        queryset=Farmer.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3 align-items-end'
        self.helper.layout = Layout(
            Row(
                Column('report_type', css_class='col-md-3'),
                Column('date_range', css_class='col-md-2'),
                Column('start_date', css_class='col-md-2'),
                Column('end_date', css_class='col-md-2'),
                Column('cluster', css_class='col-md-3'),
            ),
            Row(
                Column('farmer', css_class='col-md-3'),
                Column(
                    Div(
                        Submit('submit', 'Generate Report', css_class='btn btn-primary'),
                        HTML('<a href="." class="btn btn-secondary ms-2">Clear</a>'),
                        css_class='d-flex'
                    ),
                    css_class='col-md-9'
                ),
            )
        )

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...',
            'aria-label': 'Search'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='col-md-10'),
                Column(
                    Submit('search', 'Search', css_class='btn btn-primary w-100'),
                    css_class='col-md-2'
                )
            )
        )

class ExportForm(forms.Form):
    FORMAT_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV (.csv)'),
        ('pdf', 'PDF (.pdf)'),
    ]
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    include_all = forms.BooleanField(
        required=False,
        initial=True,
        label='Include all data'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('format', css_class='col-md-6'),
                Column(
                    Field('include_all', css_class='form-check-input'),
                    css_class='col-md-6 d-flex align-items-center'
                ),
            ),
            Div(
                Submit('export', 'Export Data', css_class='btn btn-primary'),
                css_class='d-flex justify-content-end mt-3'
            )
        )