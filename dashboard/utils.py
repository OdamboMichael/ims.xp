import pandas as pd
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
import json
from decimal import Decimal

def calculate_gross_margin(revenue, costs):
    """Calculate gross margin percentage"""
    if revenue > 0:
        return ((revenue - costs) / revenue) * 100
    return 0

def calculate_yield_per_acre(yield_data):
    """Calculate average yield per acre"""
    if yield_data.exists():
        total_yield = yield_data.aggregate(Sum('total_yield'))['total_yield__sum'] or 0
        total_area = yield_data.aggregate(Sum('area_count'))['area_count__sum'] or 0
        if total_area > 0:
            return total_yield / total_area
    return 0

def calculate_labor_efficiency(labor_data, production_data):
    """Calculate labor efficiency metric"""
    total_labor_cost = sum([lab.monthly_cost() for lab in labor_data])
    total_revenue = production_data.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    
    if total_labor_cost > 0:
        return (total_revenue / total_labor_cost) * 100
    return 0

def calculate_inventory_turnover(inventory_items, farm_inputs):
    """Calculate inventory turnover ratio"""
    total_input_cost = farm_inputs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    avg_inventory_value = inventory_items.aggregate(Avg('current_value'))['current_value__avg'] or 0
    
    if avg_inventory_value > 0:
        return total_input_cost / avg_inventory_value
    return 0

def generate_report_data(report_type, start_date, end_date, filters=None):
    """Generate data for different report types"""
    data = {
        'report_type': report_type,
        'date_range': f"{start_date} to {end_date}",
        'generated_at': timezone.now(),
    }
    
    if filters is None:
        filters = {}
    
    # Base querysets filtered by date
    production_qs = ProductionData.objects.filter(
        date_recorded__range=[start_date, end_date]
    )
    yield_qs = YieldData.objects.filter(
        date_recorded__range=[start_date, end_date]
    )
    labor_qs = Labor.objects.all()
    input_qs = FarmInput.objects.filter(
        date__range=[start_date, end_date]
    )
    
    # Apply additional filters
    if 'cluster' in filters:
        cluster = filters['cluster']
        production_qs = production_qs.filter(farm__cluster=cluster)
        yield_qs = yield_qs.filter(farm__cluster=cluster)
        labor_qs = labor_qs.filter(farm__cluster=cluster)
        input_qs = input_qs.filter(farm__cluster=cluster)
    
    if 'farmer' in filters:
        farmer = filters['farmer']
        production_qs = production_qs.filter(farm__farmer=farmer)
        yield_qs = yield_qs.filter(farm__farmer=farmer)
        labor_qs = labor_qs.filter(farm__farmer=farmer)
        input_qs = input_qs.filter(farm__farmer=farmer)
    
    if report_type == 'operational':
        data.update({
            'gross_margin': calculate_gross_margin(
                production_qs.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
                input_qs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
            ),
            'yield_per_acre': calculate_yield_per_acre(yield_qs),
            'labor_efficiency': calculate_labor_efficiency(labor_qs, production_qs),
            'inventory_turnover': calculate_inventory_turnover(
                Inventory.objects.all(), input_qs
            ),
            'total_farms': Farm.objects.count(),
            'active_farmers': Farmer.objects.filter(is_active=True).count(),
        })
    
    elif report_type == 'profitability':
        revenue_by_product = production_qs.values('product_name').annotate(
            total_revenue=Sum('total_revenue'),
            total_quantity=Sum('quantity')
        ).order_by('-total_revenue')
        
        data.update({
            'total_revenue': production_qs.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
            'total_costs': input_qs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0,
            'net_profit': (production_qs.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0) - 
                         (input_qs.aggregate(Sum('total_cost'))['total_cost__sum'] or 0),
            'revenue_by_product': list(revenue_by_product),
            'top_products': list(revenue_by_product[:5]),
        })
    
    elif report_type == 'yield':
        yield_by_crop = yield_qs.values('crop_livestock').annotate(
            avg_yield=Avg('yield_per_unit'),
            total_yield=Sum('total_yield'),
            avg_area=Avg('area_count')
        ).order_by('-total_yield')
        
        data.update({
            'total_yield': yield_qs.aggregate(Sum('total_yield'))['total_yield__sum'] or 0,
            'average_yield_per_unit': yield_qs.aggregate(Avg('yield_per_unit'))['yield_per_unit__avg'] or 0,
            'yield_by_crop': list(yield_by_crop),
            'top_performing': list(yield_by_crop[:5]),
        })
    
    elif report_type == 'labor':
        labor_by_category = labor_qs.values('category').annotate(
            count=Count('id'),
            avg_rate=Avg('hourly_rate'),
            total_cost=Sum('hourly_rate')
        )
        
        data.update({
            'total_employees': labor_qs.count(),
            'labor_by_category': list(labor_by_category),
            'total_labor_cost': sum([lab.monthly_cost() for lab in labor_qs]),
            'avg_hourly_rate': labor_qs.aggregate(Avg('hourly_rate'))['hourly_rate__avg'] or 0,
        })
    
    return data

def export_to_excel(queryset, filename, fields=None):
    """Export queryset to Excel file"""
    if fields is None:
        # Get all field names from model
        fields = [field.name for field in queryset.model._meta.fields]
    
    # Convert queryset to list of dictionaries
    data = list(queryset.values(*fields))
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create HTTP response with Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
    
    return response

def export_to_csv(queryset, filename, fields=None):
    """Export queryset to CSV file"""
    if fields is None:
        fields = [field.name for field in queryset.model._meta.fields]
    
    data = list(queryset.values(*fields))
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    df.to_csv(response, index=False)
    return response

def paginate_queryset(request, queryset, per_page=25):
    """Helper function to paginate queryset"""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = timezone.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def get_date_range(range_type):
    """Get date range based on type"""
    today = timezone.now().date()
    
    if range_type == 'today':
        start_date = today
        end_date = today
    elif range_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif range_type == 'month':
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif range_type == 'quarter':
        quarter = (today.month - 1) // 3
        start_date = today.replace(month=quarter * 3 + 1, day=1)
        if quarter == 3:  # Q4
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=(quarter + 1) * 3 + 1, day=1) - timedelta(days=1)
    elif range_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        start_date = today - timedelta(days=30)
        end_date = today
    
    return start_date, end_date

def get_chart_data(chart_type, start_date, end_date, filters=None):
    """Generate data for charts"""
    if filters is None:
        filters = {}
    
    if chart_type == 'revenue':
        # Daily revenue for the period
        revenue_data = ProductionData.objects.filter(
            date_recorded__range=[start_date, end_date]
        ).values('date_recorded').annotate(
            daily_revenue=Sum('total_revenue')
        ).order_by('date_recorded')
        
        labels = [item['date_recorded'].strftime('%b %d') for item in revenue_data]
        data = [float(item['daily_revenue'] or 0) for item in revenue_data]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Daily Revenue',
                'data': data,
                'borderColor': '#2c5530',
                'backgroundColor': 'rgba(44, 85, 48, 0.1)',
            }]
        }
    
    elif chart_type == 'yield':
        # Yield by crop type
        yield_data = YieldData.objects.filter(
            date_recorded__range=[start_date, end_date]
        ).values('crop_livestock').annotate(
            total_yield=Sum('total_yield')
        ).order_by('-total_yield')[:10]
        
        labels = [item['crop_livestock'] for item in yield_data]
        data = [float(item['total_yield'] or 0) for item in yield_data]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Total Yield',
                'data': data,
                'backgroundColor': [
                    '#2c5530', '#4a7c59', '#8fb996', '#c8e6c9',
                    '#a5d6a7', '#81c784', '#66bb6a', '#4caf50',
                    '#388e3c', '#2e7d32'
                ],
            }]
        }
    
    elif chart_type == 'labor':
        # Labor distribution by category
        labor_data = Labor.objects.values('category').annotate(
            count=Count('id')
        )
        
        labels = [item['category'].title() for item in labor_data]
        data = [item['count'] for item in labor_data]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Employees by Category',
                'data': data,
                'backgroundColor': ['#2c5530', '#4a7c59', '#8fb996', '#c8e6c9'],
            }]
        }

def send_daily_report(email, data):
    """Send daily report email"""
    # This would integrate with your email service
    pass

def backup_database():
    """Create database backup"""
    # This would create a database backup
    pass

def validate_farmer_data(data):
    """Validate farmer registration data"""
    errors = {}
    
    # Check required fields
    required_fields = ['farmer_id', 'name', 'age', 'gender', 'country']
    for field in required_fields:
        if not data.get(field):
            errors[field] = f"{field.replace('_', ' ').title()} is required"
    
    # Validate age
    if data.get('age'):
        try:
            age = int(data['age'])
            if age < 18 or age > 100:
                errors['age'] = 'Age must be between 18 and 100'
        except ValueError:
            errors['age'] = 'Age must be a valid number'
    
    # Validate email
    if data.get('email'):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(data['email'])
        except ValidationError:
            errors['email'] = 'Enter a valid email address'
    
    return errors