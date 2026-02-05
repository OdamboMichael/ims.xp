from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import json
from django.contrib.auth.models import User

from .models import (
    Institution, Cluster, Farmer, Farm, ProductionData, YieldData,
    Labor, FarmInput, Inventory, WaterInfrastructure, UtilitiesPower,
    Report, DashboardSetting
)
from .forms import (
    ClusterForm, FarmerForm, FarmForm, ProductionDataForm,
    YieldDataForm, LaborForm, FarmInputForm, InventoryForm,
    ReportFilterForm, SearchForm, ExportForm
)
from .utils import (
    generate_report_data, export_to_excel, export_to_csv,
    paginate_queryset, get_date_range, get_chart_data,
    calculate_gross_margin, calculate_yield_per_acre
)

@login_required
def user_list(request):
    """List all users (admin only)"""
    if not request.user.is_staff:
        # Redirect non-staff users
        return redirect('dashboard:home')
    
    users = User.objects.all().order_by('username')
    return render(request, 'dashboard/users/list.html', {'users': users})

@login_required
def home(request):
    """Dashboard home page with overview statistics"""
    try:
        institution = Institution.objects.get(user=request.user)
    except Institution.DoesNotExist:
        institution = None
    
    # Get date range for statistics (default: last 30 days)
    start_date = timezone.now().date() - timedelta(days=30)
    end_date = timezone.now().date()
    
    # Basic statistics
    total_farmers = Farmer.objects.count()
    total_farms = Farm.objects.count()
    total_clusters = Cluster.objects.count()
    
    # Production statistics
    production_data = ProductionData.objects.filter(
        date_recorded__range=[start_date, end_date]
    )
    total_revenue = production_data.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    
    # Yield statistics
    yield_data = YieldData.objects.filter(
        date_recorded__range=[start_date, end_date]
    )
    total_yield = yield_data.aggregate(Sum('total_yield'))['total_yield__sum'] or 0
    
    # Labor statistics
    labor_data = Labor.objects.filter(status='active')
    active_labor = labor_data.count()
    
    # Recent activity
    recent_production = ProductionData.objects.select_related('farm').order_by('-date_recorded')[:10]
    recent_yield = YieldData.objects.select_related('farm').order_by('-date_recorded')[:10]
    
    # Low inventory items
    low_inventory = Inventory.objects.filter(
        Q(status='maintenance') | Q(status='repair')
    )[:5]
    
    # Upcoming maintenance
    upcoming_maintenance = Inventory.objects.filter(
        next_maintenance__gte=timezone.now().date(),
        next_maintenance__lte=timezone.now().date() + timedelta(days=7)
    )[:5]
    
    context = {
        'institution': institution,
        'total_farmers': total_farmers,
        'total_farms': total_farms,
        'total_clusters': total_clusters,
        'total_revenue': total_revenue,
        'total_yield': total_yield,
        'active_labor': active_labor,
        'recent_production': recent_production,
        'recent_yield': recent_yield,
        'low_inventory': low_inventory,
        'upcoming_maintenance': upcoming_maintenance,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def clusters_list(request):
    """List all clusters"""
    clusters = Cluster.objects.all().order_by('name')
    form = ClusterForm(request=request)
    
    if request.method == 'POST':
        form = ClusterForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            cluster = form.save(commit=False)
            cluster.institution = Institution.objects.get(user=request.user)
            cluster.save()
            messages.success(request, f'Cluster "{cluster.name}" created successfully!')
            return redirect('dashboard:clusters_list')
    
    # Filter by search
    search_query = request.GET.get('search', '')
    if search_query:
        clusters = clusters.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        clusters = clusters.filter(is_active=True)
    elif status == 'inactive':
        clusters = clusters.filter(is_active=False)
    
    # Pagination
    page_obj = paginate_queryset(request, clusters, per_page=20)
    
    context = {
        'clusters': page_obj,
        'form': form,
        'search_form': SearchForm(initial={'query': search_query}),
        'total_clusters': clusters.count(),
        'active_clusters': clusters.filter(is_active=True).count(),
    }
    return render(request, 'dashboard/clusters/list.html', context)

@login_required
def cluster_create(request):
    """Create a new cluster"""
    if request.method == 'POST':
        form = ClusterForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            cluster = form.save(commit=False)
            cluster.institution = Institution.objects.get(user=request.user)
            cluster.save()
            messages.success(request, f'Cluster "{cluster.name}" created successfully!')
            return redirect('dashboard:cluster_detail', cluster_id=cluster.id)
    else:
        form = ClusterForm(request=request)
    
    context = {'form': form}
    return render(request, 'dashboard/clusters/create.html', context)

@login_required
def cluster_detail(request, cluster_id):
    """View cluster details"""
    cluster = get_object_or_404(Cluster, id=cluster_id)
    farmers = cluster.farmer_set.all().order_by('name')
    
    # Filter farmers
    search_query = request.GET.get('search', '')
    if search_query:
        farmers = farmers.filter(
            Q(name__icontains=search_query) |
            Q(farmer_id__icontains=search_query)
        )
    
    # Pagination for farmers
    farmers_page = paginate_queryset(request, farmers, per_page=15)
    
    # Farms in this cluster
    farms = cluster.farm_set.all()
    
    # Production data for this cluster
    production_data = ProductionData.objects.filter(farm__cluster=cluster).order_by('-date_recorded')[:10]
    
    # Statistics
    total_farmers = farmers.count()
    total_farms = farms.count()
    total_area = farms.aggregate(Sum('size'))['size__sum'] or 0
    total_revenue = ProductionData.objects.filter(farm__cluster=cluster).aggregate(
        Sum('total_revenue')
    )['total_revenue__sum'] or 0
    
    context = {
        'cluster': cluster,
        'farmers': farmers_page,
        'farms': farms,
        'production_data': production_data,
        'total_farmers': total_farmers,
        'total_farms': total_farms,
        'total_area': total_area,
        'total_revenue': total_revenue,
        'search_form': SearchForm(initial={'query': search_query}),
    }
    return render(request, 'dashboard/clusters/detail.html', context)

@login_required
def cluster_edit(request, cluster_id):
    """Edit cluster details"""
    cluster = get_object_or_404(Cluster, id=cluster_id)
    
    if request.method == 'POST':
        form = ClusterForm(request.POST, request.FILES, instance=cluster, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cluster "{cluster.name}" updated successfully!')
            return redirect('dashboard:cluster_detail', cluster_id=cluster.id)
    else:
        form = ClusterForm(instance=cluster, request=request)
    
    context = {
        'form': form,
        'cluster': cluster,
    }
    return render(request, 'dashboard/clusters/edit.html', context)

@login_required
def cluster_delete(request, cluster_id):
    """Delete a cluster"""
    cluster = get_object_or_404(Cluster, id=cluster_id)
    
    if request.method == 'POST':
        cluster_name = cluster.name
        cluster.delete()
        messages.success(request, f'Cluster "{cluster_name}" deleted successfully!')
        return redirect('dashboard:clusters_list')
    
    context = {'cluster': cluster}
    return render(request, 'dashboard/clusters/delete.html', context)

@login_required
def cluster_add_farmer(request, cluster_id):
    """Add farmer to cluster"""
    cluster = get_object_or_404(Cluster, id=cluster_id)
    
    if request.method == 'POST':
        farmer_id = request.POST.get('farmer_id')
        try:
            farmer = Farmer.objects.get(farmer_id=farmer_id)
            # Check if farmer is already in cluster
            if not cluster.farmer_set.filter(id=farmer.id).exists():
                cluster.farmer_set.add(farmer)
                messages.success(request, f'Farmer "{farmer.name}" added to cluster successfully!')
            else:
                messages.warning(request, f'Farmer "{farmer.name}" is already in this cluster.')
        except Farmer.DoesNotExist:
            messages.error(request, f'Farmer with ID "{farmer_id}" not found.')
        
        return redirect('dashboard:cluster_detail', cluster_id=cluster.id)
    
    context = {'cluster': cluster}
    return render(request, 'dashboard/clusters/add_farmer.html', context)

@login_required
def cluster_remove_farmer(request, cluster_id, farmer_id):
    """Remove farmer from cluster"""
    cluster = get_object_or_404(Cluster, id=cluster_id)
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    if request.method == 'POST':
        if cluster.farmer_set.filter(id=farmer.id).exists():
            cluster.farmer_set.remove(farmer)
            messages.success(request, f'Farmer "{farmer.name}" removed from cluster successfully!')
        else:
            messages.warning(request, f'Farmer "{farmer.name}" is not in this cluster.')
        
        return redirect('dashboard:cluster_detail', cluster_id=cluster.id)
    
    context = {
        'cluster': cluster,
        'farmer': farmer,
    }
    return render(request, 'dashboard/clusters/remove_farmer.html', context)

@login_required
def farms_list(request):
    """List all farms"""
    farms = Farm.objects.select_related('farmer', 'cluster').all().order_by('name')
    form = FarmForm(request=request)
    
    if request.method == 'POST':
        form = FarmForm(request.POST, request=request)
        if form.is_valid():
            farm = form.save()
            messages.success(request, f'Farm "{farm.name}" created successfully!')
            return redirect('dashboard:farms_list')
    
    # Filtering
    search_query = request.GET.get('search', '')
    region = request.GET.get('region', '')
    cluster = request.GET.get('cluster', '')
    production_type = request.GET.get('production_type', '')
    
    if search_query:
        farms = farms.filter(
            Q(name__icontains=search_query) |
            Q(farmer__name__icontains=search_query)
        )
    
    if region and region != 'all':
        farms = farms.filter(county=region)
    
    if cluster and cluster != 'all':
        farms = farms.filter(cluster__name=cluster)
    
    if production_type and production_type != 'all':
        farms = farms.filter(production_type=production_type)
    
    # Size filter
    min_size = request.GET.get('min_size')
    max_size = request.GET.get('max_size')
    if min_size:
        farms = farms.filter(size__gte=min_size)
    if max_size:
        farms = farms.filter(size__lte=max_size)
    
    # Pagination
    page_obj = paginate_queryset(request, farms, per_page=25)
    
    context = {
        'farms': page_obj,
        'form': form,
        'search_form': SearchForm(initial={'query': search_query}),
        'regions': Farm.objects.values_list('county', flat=True).distinct(),
        'clusters': Cluster.objects.all(),
        'production_types': dict(Farm.PRODUCTION_TYPES),
        'total_farms': farms.count(),
        'total_area': farms.aggregate(Sum('size'))['size__sum'] or 0,
    }
    return render(request, 'dashboard/farms/list.html', context)

@login_required
def farm_create(request):
    """Create a new farm"""
    if request.method == 'POST':
        form = FarmForm(request.POST, request=request)
        if form.is_valid():
            farm = form.save()
            messages.success(request, f'Farm "{farm.name}" created successfully!')
            return redirect('dashboard:farm_detail', farm_id=farm.id)
    else:
        form = FarmForm(request=request)
    
    context = {'form': form}
    return render(request, 'dashboard/farms/create.html', context)

@login_required
def farm_detail(request, farm_id):
    """View farm details"""
    farm = get_object_or_404(Farm, id=farm_id)
    
    # Production data for this farm
    production_data = ProductionData.objects.filter(farm=farm).order_by('-date_recorded')[:10]
    yield_data = YieldData.objects.filter(farm=farm).order_by('-date_recorded')[:10]
    labor_data = Labor.objects.filter(farm=farm).order_by('-date_hired')
    inputs_data = FarmInput.objects.filter(farm=farm).order_by('-date')[:10]
    inventory_items = Inventory.objects.filter(farm=farm).order_by('-purchase_date')
    
    # Statistics
    total_revenue = ProductionData.objects.filter(farm=farm).aggregate(
        Sum('total_revenue')
    )['total_revenue__sum'] or 0
    
    total_input_cost = FarmInput.objects.filter(farm=farm).aggregate(
        Sum('total_cost')
    )['total_cost__sum'] or 0
    
    total_labor_cost = sum([lab.monthly_cost() for lab in labor_data])
    
    context = {
        'farm': farm,
        'production_data': production_data,
        'yield_data': yield_data,
        'labor_data': labor_data,
        'inputs_data': inputs_data,
        'inventory_items': inventory_items,
        'total_revenue': total_revenue,
        'total_input_cost': total_input_cost,
        'total_labor_cost': total_labor_cost,
        'gross_margin': calculate_gross_margin(total_revenue, total_input_cost + total_labor_cost),
    }
    return render(request, 'dashboard/farms/detail.html', context)

@login_required
def farm_edit(request, farm_id):
    """Edit farm details"""
    farm = get_object_or_404(Farm, id=farm_id)
    
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, f'Farm "{farm.name}" updated successfully!')
            return redirect('dashboard:farm_detail', farm_id=farm.id)
    else:
        form = FarmForm(instance=farm, request=request)
    
    context = {
        'form': form,
        'farm': farm,
    }
    return render(request, 'dashboard/farms/edit.html', context)

@login_required
def farm_delete(request, farm_id):
    """Delete a farm"""
    farm = get_object_or_404(Farm, id=farm_id)
    
    if request.method == 'POST':
        farm_name = farm.name
        farm.delete()
        messages.success(request, f'Farm "{farm_name}" deleted successfully!')
        return redirect('dashboard:farms_list')
    
    context = {'farm': farm}
    return render(request, 'dashboard/farms/delete.html', context)

@login_required
def farmers_list(request):
    """List all farmers"""
    farmers = Farmer.objects.all().order_by('name')
    form = FarmerForm()
    
    if request.method == 'POST':
        form = FarmerForm(request.POST, request.FILES)
        if form.is_valid():
            farmer = form.save()
            messages.success(request, f'Farmer "{farmer.name}" added successfully!')
            return redirect('dashboard:farmers_list')
    
    # Filtering
    search_query = request.GET.get('search', '')
    country = request.GET.get('country', '')
    constituency = request.GET.get('constituency', '')
    ward = request.GET.get('ward', '')
    gender = request.GET.get('gender', '')
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')
    min_years = request.GET.get('min_years')
    max_years = request.GET.get('max_years')
    
    if search_query:
        farmers = farmers.filter(
            Q(name__icontains=search_query) |
            Q(farmer_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if country and country != 'all':
        farmers = farmers.filter(country=country)
    
    if constituency and constituency != 'all':
        farmers = farmers.filter(constituency=constituency)
    
    if ward and ward != 'all':
        farmers = farmers.filter(ward=ward)
    
    if gender and gender != 'all':
        farmers = farmers.filter(gender=gender)
    
    if min_age:
        farmers = farmers.filter(age__gte=min_age)
    if max_age:
        farmers = farmers.filter(age__lte=max_age)
    
    if min_years:
        farmers = farmers.filter(years_farming__gte=min_years)
    if max_years:
        farmers = farmers.filter(years_farming__lte=max_years)
    
    # Pagination
    page_obj = paginate_queryset(request, farmers, per_page=25)
    
    context = {
        'farmers': page_obj,
        'form': form,
        'search_form': SearchForm(initial={'query': search_query}),
        'countries': Farmer.objects.values_list('country', flat=True).distinct(),
        'constituencies': Farmer.objects.values_list('constituency', flat=True).distinct(),
        'wards': Farmer.objects.values_list('ward', flat=True).distinct(),
        'total_farmers': farmers.count(),
        'male_farmers': farmers.filter(gender='male').count(),
        'female_farmers': farmers.filter(gender='female').count(),
        'avg_age': farmers.aggregate(Avg('age'))['age__avg'] or 0,
        'avg_experience': farmers.aggregate(Avg('years_farming'))['years_farming__avg'] or 0,
    }
    return render(request, 'dashboard/farmers/list.html', context)

@login_required
def farmer_create(request):
    """Create a new farmer"""
    if request.method == 'POST':
        form = FarmerForm(request.POST, request.FILES)
        if form.is_valid():
            farmer = form.save()
            messages.success(request, f'Farmer "{farmer.name}" added successfully!')
            return redirect('dashboard:farmer_detail', farmer_id=farmer.id)
    else:
        form = FarmerForm()
    
    context = {'form': form}
    return render(request, 'dashboard/farmers/create.html', context)

@login_required
def farmer_detail(request, farmer_id):
    """View farmer details"""
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farms = Farm.objects.filter(farmer=farmer)
    clusters = farmer.clusters.all()
    
    # Production data for farmer's farms
    production_data = ProductionData.objects.filter(farm__farmer=farmer).order_by('-date_recorded')[:10]
    yield_data = YieldData.objects.filter(farm__farmer=farmer).order_by('-date_recorded')[:10]
    
    # Statistics
    total_farms = farms.count()
    total_area = farms.aggregate(Sum('size'))['size__sum'] or 0
    total_revenue = ProductionData.objects.filter(farm__farmer=farmer).aggregate(
        Sum('total_revenue')
    )['total_revenue__sum'] or 0
    
    context = {
        'farmer': farmer,
        'farms': farms,
        'clusters': clusters,
        'production_data': production_data,
        'yield_data': yield_data,
        'total_farms': total_farms,
        'total_area': total_area,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard/farmers/detail.html', context)

@login_required
def farmer_edit(request, farmer_id):
    """Edit farmer details"""
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    if request.method == 'POST':
        form = FarmerForm(request.POST, request.FILES, instance=farmer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Farmer "{farmer.name}" updated successfully!')
            return redirect('dashboard:farmer_detail', farmer_id=farmer.id)
    else:
        form = FarmerForm(instance=farmer)
    
    context = {
        'form': form,
        'farmer': farmer,
    }
    return render(request, 'dashboard/farmers/edit.html', context)

@login_required
def farmer_delete(request, farmer_id):
    """Delete a farmer"""
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    if request.method == 'POST':
        farmer_name = farmer.name
        farmer.delete()
        messages.success(request, f'Farmer "{farmer_name}" deleted successfully!')
        return redirect('dashboard:farmers_list')
    
    context = {'farmer': farmer}
    return render(request, 'dashboard/farmers/delete.html', context)

@login_required
def production_overview(request):
    """Production data overview"""
    production_data = ProductionData.objects.select_related('farm').all().order_by('-date_recorded')
    yield_data = YieldData.objects.select_related('farm').all().order_by('-date_recorded')
    
    # Filter by date range
    date_range = request.GET.get('date_range', 'month')
    start_date, end_date = get_date_range(date_range)
    
    production_data = production_data.filter(
        date_recorded__range=[start_date, end_date]
    )
    yield_data = yield_data.filter(
        date_recorded__range=[start_date, end_date]
    )
    
    # Summary statistics
    total_revenue = production_data.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    total_yield = yield_data.aggregate(Sum('total_yield'))['total_yield__sum'] or 0
    avg_yield_per_unit = yield_data.aggregate(Avg('yield_per_unit'))['yield_per_unit__avg'] or 0
    total_products = production_data.values('product_name').distinct().count()
    
    # Top products by revenue
    top_products = production_data.values('product_name').annotate(
        total_revenue=Sum('total_revenue'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')[:5]
    
    # Pagination
    production_page = paginate_queryset(request, production_data, per_page=20)
    yield_page = paginate_queryset(request, yield_data, per_page=20)
    
    context = {
        'production_data': production_page,
        'yield_data': yield_page,
        'total_revenue': total_revenue,
        'total_yield': total_yield,
        'avg_yield_per_unit': avg_yield_per_unit,
        'total_products': total_products,
        'top_products': top_products,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/production/overview.html', context)

@login_required
def sales_revenue(request):
    """Sales and revenue data"""
    sales_data = ProductionData.objects.select_related('farm').all().order_by('-date_recorded')
    
    # Filter by date range
    date_range = request.GET.get('date_range', 'month')
    start_date, end_date = get_date_range(date_range)
    
    sales_data = sales_data.filter(date_recorded__range=[start_date, end_date])
    
    # Sales by product
    sales_by_product = sales_data.values('product_name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_revenue'),
        avg_price=Avg('price_per_unit')
    ).order_by('-total_revenue')
    
    # Monthly revenue trend
    monthly_revenue = sales_data.extra({
        'month': "EXTRACT(month FROM date_recorded)",
        'year': "EXTRACT(year FROM date_recorded)"
    }).values('year', 'month').annotate(
        monthly_total=Sum('total_revenue'),
        monthly_quantity=Sum('quantity')
    ).order_by('year', 'month')
    
    # Top customers (farms)
    top_customers = sales_data.values('farm__name', 'farm__farmer__name').annotate(
        total_revenue=Sum('total_revenue'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')[:10]
    
    # Pagination
    sales_page = paginate_queryset(request, sales_data, per_page=25)
    
    context = {
        'sales_data': sales_page,
        'sales_by_product': sales_by_product,
        'monthly_revenue': list(monthly_revenue),
        'top_customers': top_customers,
        'total_revenue': sales_data.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
        'total_quantity': sales_data.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'avg_price': sales_data.aggregate(Avg('price_per_unit'))['price_per_unit__avg'] or 0,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/production/sales_revenue.html', context)

@login_required
def sales_create(request):
    """Create sales/production record"""
    if request.method == 'POST':
        form = ProductionDataForm(request.POST)
        if form.is_valid():
            sales_record = form.save()
            messages.success(request, 'Sales data added successfully!')
            return redirect('dashboard:sales_revenue')
    else:
        form = ProductionDataForm()
    
    context = {'form': form}
    return render(request, 'dashboard/production/sales_create.html', context)

@login_required
def yield_data(request):
    """Yield data analysis"""
    yield_data = YieldData.objects.select_related('farm').all().order_by('-date_recorded')
    
    # Filter by date range
    date_range = request.GET.get('date_range', 'month')
    start_date, end_date = get_date_range(date_range)
    
    yield_data = yield_data.filter(date_recorded__range=[start_date, end_date])
    
    # Yield analysis
    yield_by_crop = yield_data.values('crop_livestock').annotate(
        avg_yield=Avg('yield_per_unit'),
        total_yield=Sum('total_yield'),
        total_area=Sum('area_count'),
        count=Count('id')
    ).order_by('-total_yield')
    
    # Yield by farm
    yield_by_farm = yield_data.values('farm__name', 'farm__farmer__name').annotate(
        total_yield=Sum('total_yield'),
        avg_yield_per_unit=Avg('yield_per_unit')
    ).order_by('-total_yield')[:10]
    
    # Quality distribution
    quality_distribution = yield_data.values('quality_grade').annotate(
        count=Count('id'),
        avg_yield=Avg('yield_per_unit')
    ).order_by('quality_grade')
    
    # Pagination
    yield_page = paginate_queryset(request, yield_data, per_page=25)
    
    context = {
        'yield_data': yield_page,
        'yield_by_crop': yield_by_crop,
        'yield_by_farm': yield_by_farm,
        'quality_distribution': quality_distribution,
        'total_yield': yield_data.aggregate(Sum('total_yield'))['total_yield__sum'] or 0,
        'avg_yield_per_unit': yield_data.aggregate(Avg('yield_per_unit'))['yield_per_unit__avg'] or 0,
        'total_area': yield_data.aggregate(Sum('area_count'))['area_count__sum'] or 0,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/production/yield_data.html', context)

@login_required
def yield_create(request):
    """Create yield record"""
    if request.method == 'POST':
        form = YieldDataForm(request.POST)
        if form.is_valid():
            yield_record = form.save()
            messages.success(request, 'Yield data added successfully!')
            return redirect('dashboard:yield_data')
    else:
        form = YieldDataForm()
    
    context = {'form': form}
    return render(request, 'dashboard/production/yield_create.html', context)

@login_required
def labor_management(request):
    """Labor management"""
    labor_data = Labor.objects.select_related('farm').all().order_by('-date_hired')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        labor_data = labor_data.filter(status=status)
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        labor_data = labor_data.filter(category=category)
    
    # Labor statistics
    labor_stats = labor_data.aggregate(
        total_employees=Count('id'),
        total_permanent=Count('id', filter=Q(category='permanent')),
        total_casual=Count('id', filter=Q(category='casual')),
        total_seasonal=Count('id', filter=Q(category='seasonal')),
        avg_hourly_rate=Avg('hourly_rate'),
        total_weekly_hours=Sum('hours_per_week')
    )
    
    # Labor cost distribution
    labor_cost_by_category = labor_data.values('category').annotate(
        total_cost=Sum('hourly_rate'),
        count=Count('id'),
        avg_rate=Avg('hourly_rate')
    )
    
    # Monthly labor cost trend
    monthly_labor_cost = []
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i < 5:
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            month_end = month_start + timedelta(days=31)
        
        month_labor = Labor.objects.filter(date_hired__lte=month_end)
        if status:
            month_labor = month_labor.filter(status=status)
        if category:
            month_labor = month_labor.filter(category=category)
        
        monthly_cost = sum([lab.monthly_cost() for lab in month_labor])
        monthly_labor_cost.append({
            'month': month_start.strftime('%b %Y'),
            'cost': monthly_cost
        })
    
    monthly_labor_cost.reverse()
    
    # Pagination
    labor_page = paginate_queryset(request, labor_data, per_page=25)
    
    context = {
        'labor_data': labor_page,
        'labor_stats': labor_stats,
        'labor_cost_by_category': labor_cost_by_category,
        'monthly_labor_cost': monthly_labor_cost,
        'total_weekly_cost': sum([lab.weekly_cost() for lab in labor_data]),
        'total_monthly_cost': sum([lab.monthly_cost() for lab in labor_data]),
    }
    return render(request, 'dashboard/production/labor.html', context)

@login_required
def labor_create(request):
    """Create labor record"""
    if request.method == 'POST':
        form = LaborForm(request.POST)
        if form.is_valid():
            labor = form.save()
            messages.success(request, f'Labor record for {labor.employee_name} added successfully!')
            return redirect('dashboard:labor')
    else:
        form = LaborForm()
    
    context = {'form': form}
    return render(request, 'dashboard/production/labor_create.html', context)

@login_required
def farm_inputs(request):
    """Farm inputs management"""
    inputs_data = FarmInput.objects.select_related('farm').all().order_by('-date')
    
    # Filter by date range
    date_range = request.GET.get('date_range', 'month')
    start_date, end_date = get_date_range(date_range)
    
    inputs_data = inputs_data.filter(date__range=[start_date, end_date])
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        inputs_data = inputs_data.filter(category=category)
    
    # Input cost analysis
    input_cost_by_category = inputs_data.values('category').annotate(
        total_cost=Sum('total_cost'),
        total_quantity=Sum('quantity'),
        avg_unit_cost=Avg('unit_cost')
    ).order_by('-total_cost')
    
    # Top suppliers
    top_suppliers = inputs_data.exclude(supplier='').values('supplier').annotate(
        total_cost=Sum('total_cost'),
        total_transactions=Count('id')
    ).order_by('-total_cost')[:10]
    
    # Monthly input cost trend
    monthly_input_cost = inputs_data.extra({
        'month': "EXTRACT(month FROM date)",
        'year': "EXTRACT(year FROM date)"
    }).values('year', 'month').annotate(
        monthly_total=Sum('total_cost'),
        monthly_quantity=Sum('quantity')
    ).order_by('year', 'month')
    
    # Pagination
    inputs_page = paginate_queryset(request, inputs_data, per_page=25)
    
    context = {
        'inputs_data': inputs_page,
        'input_cost_by_category': input_cost_by_category,
        'top_suppliers': top_suppliers,
        'monthly_input_cost': list(monthly_input_cost),
        'total_cost': inputs_data.aggregate(Sum('total_cost'))['total_cost__sum'] or 0,
        'total_quantity': inputs_data.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'avg_unit_cost': inputs_data.aggregate(Avg('unit_cost'))['unit_cost__avg'] or 0,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/production/inputs.html', context)

@login_required
def inputs_create(request):
    """Create farm input record"""
    if request.method == 'POST':
        form = FarmInputForm(request.POST)
        if form.is_valid():
            farm_input = form.save()
            messages.success(request, 'Farm input recorded successfully!')
            return redirect('dashboard:inputs')
    else:
        form = FarmInputForm()
    
    context = {'form': form}
    return render(request, 'dashboard/production/inputs_create.html', context)

@login_required
def inventory_management(request):
    """Inventory management"""
    inventory_items = Inventory.objects.select_related('farm').all().order_by('-purchase_date')
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        inventory_items = inventory_items.filter(category=category)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        inventory_items = inventory_items.filter(status=status)
    
    # Inventory value by category
    inventory_value = inventory_items.values('category').annotate(
        total_value=Sum('cost'),
        current_value=Sum('current_value'),
        item_count=Count('id'),
        avg_depreciation=Avg('depreciation_rate')
    ).order_by('-total_value')
    
    # Items needing maintenance
    maintenance_needed = inventory_items.filter(
        Q(status='maintenance') | Q(status='repair') |
        Q(next_maintenance__lte=timezone.now().date() + timedelta(days=30))
    )
    
    # Depreciation analysis
    depreciation_analysis = []
    for item in inventory_items:
        if item.current_value and item.purchase_date:
            years_owned = (timezone.now().date() - item.purchase_date).days / 365.25
            depreciation = ((item.cost - item.current_value) / item.cost) * 100 if item.cost > 0 else 0
            depreciation_analysis.append({
                'item': item.item_name,
                'purchase_date': item.purchase_date,
                'cost': item.cost,
                'current_value': item.current_value,
                'years_owned': years_owned,
                'depreciation': depreciation
            })
    
    # Pagination
    inventory_page = paginate_queryset(request, inventory_items, per_page=25)
    
    context = {
        'inventory_items': inventory_page,
        'inventory_value': inventory_value,
        'maintenance_needed': maintenance_needed,
        'depreciation_analysis': depreciation_analysis[:10],
        'total_value': inventory_items.aggregate(Sum('cost'))['cost__sum'] or 0,
        'total_current_value': inventory_items.aggregate(Sum('current_value'))['current_value__sum'] or 0,
        'total_items': inventory_items.count(),
    }
    return render(request, 'dashboard/production/inventory.html', context)

@login_required
def inventory_create(request):
    """Create inventory record"""
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            inventory_item = form.save()
            messages.success(request, f'Inventory item "{inventory_item.item_name}" added successfully!')
            return redirect('dashboard:inventory')
    else:
        form = InventoryForm()
    
    context = {'form': form}
    return render(request, 'dashboard/production/inventory_create.html', context)

@login_required
def reports_main(request):
    """Main reports page"""
    reports = Report.objects.filter(institution__user=request.user).order_by('-date_generated')
    form = ReportFilterForm(request.GET or None, request=request)
    
    report_data = None
    if form.is_valid():
        report_type = form.cleaned_data.get('report_type')
        date_range = form.cleaned_data.get('date_range')
        cluster = form.cleaned_data.get('cluster')
        farmer = form.cleaned_data.get('farmer')
        
        if report_type or date_range or cluster or farmer:
            # Get date range
            if date_range:
                start_date, end_date = get_date_range(date_range)
            else:
                start_date = timezone.now().date() - timedelta(days=30)
                end_date = timezone.now().date()
            
            # Generate report data
            filters = {}
            if cluster:
                filters['cluster'] = cluster
            if farmer:
                filters['farmer'] = farmer
            
            report_data = generate_report_data(
                report_type or 'operational',
                start_date,
                end_date,
                filters
            )
    
    # Pagination
    reports_page = paginate_queryset(request, reports, per_page=15)
    
    context = {
        'reports': reports_page,
        'form': form,
        'report_data': report_data,
        'total_reports': reports.count(),
    }
    return render(request, 'dashboard/reports/main.html', context)

@login_required
def report_generate(request):
    """Generate a new report"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_range = request.POST.get('date_range')
        title = request.POST.get('title')
        
        if not all([report_type, date_range, title]):
            messages.error(request, 'Please fill all required fields.')
            return redirect('dashboard:reports_main')
        
        try:
            institution = Institution.objects.get(user=request.user)
            start_date, end_date = get_date_range(date_range)
            
            # Generate report data
            report_data = generate_report_data(report_type, start_date, end_date)
            
            # Create report record
            report = Report.objects.create(
                title=title,
                report_type=report_type,
                institution=institution,
                generated_by=request.user,
                date_range_start=start_date,
                date_range_end=end_date,
                data_sources=report_data.get('data_sources', {}),
                insights=report_data.get('insights', {}),
                recommendations=report_data.get('recommendations', '')
            )
            
            messages.success(request, f'Report "{title}" generated successfully!')
            return redirect('dashboard:report_detail', report_id=report.id)
            
        except Institution.DoesNotExist:
            messages.error(request, 'Institution not found.')
        except Exception as e:
            messages.error(request, f'Error generating report: {str(e)}')
    
    context = {
        'report_types': dict(Report.REPORT_TYPES),
    }
    return render(request, 'dashboard/reports/generate.html', context)

@login_required
def report_detail(request, report_id):
    """View report details"""
    report = get_object_or_404(Report, id=report_id)
    
    # Check if user has permission to view this report
    if report.institution.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('dashboard:reports_main')
    
    context = {
        'report': report,
        'insights': json.loads(json.dumps(report.insights)),
        'data_sources': json.loads(json.dumps(report.data_sources)),
    }
    return render(request, 'dashboard/reports/detail.html', context)

@login_required
def report_download(request, report_id):
    """Download report file"""
    report = get_object_or_404(Report, id=report_id)
    
    if report.file_path and report.file_path.name:
        response = HttpResponse(report.file_path.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'
        return response
    else:
        messages.error(request, 'Report file not found.')
        return redirect('dashboard:report_detail', report_id=report.id)

@login_required
def report_delete(request, report_id):
    """Delete a report"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        report_title = report.title
        report.delete()
        messages.success(request, f'Report "{report_title}" deleted successfully!')
        return redirect('dashboard:reports_main')
    
    context = {'report': report}
    return render(request, 'dashboard/reports/delete.html', context)

@login_required
def settings_view(request):
    """Main settings page"""
    try:
        institution = Institution.objects.get(user=request.user)
    except Institution.DoesNotExist:
        institution = None
    
    try:
        dashboard_settings = DashboardSetting.objects.get(user=request.user)
    except DashboardSetting.DoesNotExist:
        dashboard_settings = DashboardSetting.objects.create(user=request.user)
    
    context = {
        'institution': institution,
        'dashboard_settings': dashboard_settings,
    }
    return render(request, 'dashboard/settings/main.html', context)

@login_required
def profile_settings(request):
    """Profile settings"""
    from accounts.models import UserProfile
    from accounts.forms import ProfileUpdateForm, UserProfileForm
    
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('dashboard:profile_settings')
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'dashboard/settings/profile.html', context)

@login_required
def display_settings(request):
    """Display settings"""
    try:
        dashboard_settings = DashboardSetting.objects.get(user=request.user)
    except DashboardSetting.DoesNotExist:
        dashboard_settings = DashboardSetting.objects.create(user=request.user)
    
    if request.method == 'POST':
        dashboard_settings.default_date_range = request.POST.get('default_date_range', 'month')
        dashboard_settings.show_charts = 'show_charts' in request.POST
        dashboard_settings.show_notifications = 'show_notifications' in request.POST
        dashboard_settings.items_per_page = int(request.POST.get('items_per_page', 25))
        dashboard_settings.theme = request.POST.get('theme', 'light')
        dashboard_settings.save()
        
        messages.success(request, 'Display settings updated successfully.')
        return redirect('dashboard:display_settings')
    
    context = {
        'dashboard_settings': dashboard_settings,
        'date_range_options': [
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year'),
        ],
        'theme_options': [
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
    }
    return render(request, 'dashboard/settings/display.html', context)

@login_required
def export_farms(request):
    """Export farms data"""
    farms = Farm.objects.select_related('farmer', 'cluster').all()
    return export_to_excel(farms, 'farms_export.xlsx')

@login_required
def export_farmers(request):
    """Export farmers data"""
    farmers = Farmer.objects.all()
    return export_to_excel(farmers, 'farmers_export.xlsx')

@login_required
def export_production(request):
    """Export production data"""
    production_data = ProductionData.objects.select_related('farm').all()
    return export_to_excel(production_data, 'production_export.xlsx')

@login_required
def export_yield(request):
    """Export yield data"""
    yield_data = YieldData.objects.select_related('farm').all()
    return export_to_excel(yield_data, 'yield_export.xlsx')

@login_required
def export_report(request, report_id):
    """Export report"""
    report = get_object_or_404(Report, id=report_id)
    
    # Convert report data to DataFrame
    data = {
        'title': [report.title],
        'report_type': [report.report_type],
        'date_generated': [report.date_generated],
        'date_range': [f"{report.date_range_start} to {report.date_range_end}"],
        'insights': [json.dumps(report.insights)],
        'recommendations': [report.recommendations or ''],
    }
    
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="report_{report.id}.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Report', index=False)
    
    return response

@login_required
def global_search(request):
    """Global search functionality"""
    query = request.GET.get('q', '')
    results = {}
    
    if query:
        # Search clusters
        clusters = Cluster.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )[:5]
        
        # Search farmers
        farmers = Farmer.objects.filter(
            Q(name__icontains=query) |
            Q(farmer_id__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )[:5]
        
        # Search farms
        farms = Farm.objects.filter(
            Q(name__icontains=query) |
            Q(farmer__name__icontains=query)
        )[:5]
        
        results = {
            'clusters': clusters,
            'farmers': farmers,
            'farms': farms,
            'total_results': clusters.count() + farmers.count() + farms.count(),
        }
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'dashboard/search.html', context)

@login_required
def notifications(request):
    """Notifications page"""
    # Get notifications (this would come from a Notification model)
    notifications = []  # Placeholder
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required
def help_center(request):
    """Help center"""
    context = {}
    return render(request, 'dashboard/help.html', context)

# API Views
@login_required
def api_cluster_stats(request):
    """API endpoint for cluster statistics"""
    clusters = Cluster.objects.all()
    
    stats = {
        'total_clusters': clusters.count(),
        'active_clusters': clusters.filter(is_active=True).count(),
        'total_farmers': clusters.aggregate(Sum('total_farmers'))['total_farmers__sum'] or 0,
        'total_area': float(clusters.aggregate(Sum('total_area'))['total_area__sum'] or 0),
    }
    
    return JsonResponse(stats)

@login_required
def api_farmer_stats(request):
    """API endpoint for farmer statistics"""
    farmers = Farmer.objects.all()
    
    stats = {
        'total_farmers': farmers.count(),
        'active_farmers': farmers.filter(is_active=True).count(),
        'male_farmers': farmers.filter(gender='male').count(),
        'female_farmers': farmers.filter(gender='female').count(),
        'avg_age': farmers.aggregate(Avg('age'))['age__avg'] or 0,
        'avg_experience': farmers.aggregate(Avg('years_farming'))['years_farming__avg'] or 0,
    }
    
    return JsonResponse(stats)

@login_required
def api_production_chart(request):
    """API endpoint for production chart data"""
    chart_type = request.GET.get('type', 'revenue')
    date_range = request.GET.get('range', 'month')
    
    start_date, end_date = get_date_range(date_range)
    chart_data = get_chart_data(chart_type, start_date, end_date)
    
    return JsonResponse(chart_data)

@login_required
def api_yield_chart(request):
    """API endpoint for yield chart data"""
    date_range = request.GET.get('range', 'month')
    start_date, end_date = get_date_range(date_range)
    
    # Get yield data by crop
    yield_data = YieldData.objects.filter(
        date_recorded__range=[start_date, end_date]
    ).values('crop_livestock').annotate(
        total_yield=Sum('total_yield')
    ).order_by('-total_yield')[:10]
    
    labels = [item['crop_livestock'] for item in yield_data]
    data = [float(item['total_yield'] or 0) for item in yield_data]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Yield by Crop',
            'data': data,
            'backgroundColor': [
                '#2c5530', '#4a7c59', '#8fb996', '#c8e6c9',
                '#a5d6a7', '#81c784', '#66bb6a', '#4caf50',
                '#388e3c', '#2e7d32'
            ],
        }]
    }
    
    return JsonResponse(chart_data)

@login_required
def api_revenue_chart(request):
    """API endpoint for revenue chart data"""
    date_range = request.GET.get('range', 'month')
    start_date, end_date = get_date_range(date_range)
    
    # Get daily revenue
    revenue_data = ProductionData.objects.filter(
        date_recorded__range=[start_date, end_date]
    ).extra({
        'day': "DATE(date_recorded)"
    }).values('day').annotate(
        daily_revenue=Sum('total_revenue')
    ).order_by('day')
    
    labels = [item['day'].strftime('%b %d') for item in revenue_data]
    data = [float(item['daily_revenue'] or 0) for item in revenue_data]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Daily Revenue',
            'data': data,
            'borderColor': '#2c5530',
            'backgroundColor': 'rgba(44, 85, 48, 0.1)',
            'fill': True,
            'tension': 0.4,
        }]
    }
    
    return JsonResponse(chart_data)

# In dashboard/views.py, add these functions:

def error_400(request, exception=None):
    """Handler for 400 Bad Request"""
    return render(request, '400.html', status=400)

def error_403(request, exception=None):
    """Handler for 403 Forbidden"""
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    """Handler for 404 Not Found"""
    return render(request, '404.html', status=404)

def error_500(request, exception=None):
    """Handler for 500 Server Error"""
    return render(request, '500.html', status=500)



def reports_main(request):
    return render(request, 'dashboard/reports/main.html')

def reports_operational(request):
    return render(request, 'dashboard/reports/operational.html')

def reports_productivity(request):
    return render(request, 'dashboard/reports/productivity.html')

def reports_profitability(request):
    return render(request, 'dashboard/reports/profitability.html')

def reports_sales_insights(request):
    return render(request, 'dashboard/reports/sales_insights.html')

def reports_vine(request):
    return render(request, 'dashboard/reports/vine_reports.html')
