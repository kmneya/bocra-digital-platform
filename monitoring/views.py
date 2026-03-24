from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
from .models import TelecomProvider, NetworkQualityMetrics, NetworkIncident, SpectrumAnalysis
from django.db.models import Avg, Count, Q
import random
import json

@login_required
def network_monitoring_dashboard(request):
    """Network Quality Monitoring Dashboard for Officers"""
    
    # Get all providers
    providers = TelecomProvider.objects.all()
    
    # If no providers exist, create dummy data
    if not providers.exists():
        create_dummy_providers()
        providers = TelecomProvider.objects.all()
    
    # Get latest metrics for each provider
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    
    # Prepare data for charts
    provider_data = []
    for provider in providers:
        # Get today's metrics
        today_metrics = NetworkQualityMetrics.objects.filter(
            provider=provider,
            date=today
        ).first()
        
        # Get average metrics for last 7 days
        weekly_avg = NetworkQualityMetrics.objects.filter(
            provider=provider,
            date__gte=last_7_days
        ).aggregate(
            avg_call_drop=Avg('call_drop_rate'),
            avg_latency=Avg('latency'),
            avg_throughput=Avg('avg_throughput'),
            avg_uptime=Avg('uptime_percentage')
        )
        
        # Get active incidents
        active_incidents = NetworkIncident.objects.filter(
            provider=provider,
            is_resolved=False
        ).count()
        
        provider_data.append({
            'provider': provider,
            'today_metrics': today_metrics,
            'weekly_avg': weekly_avg,
            'active_incidents': active_incidents,
        })
    
    # Get all active incidents
    active_incidents_list = NetworkIncident.objects.filter(
        is_resolved=False
    ).order_by('-start_time')[:10]
    
    # Get recent incidents for timeline
    recent_incidents = NetworkIncident.objects.filter(
        start_time__gte=last_7_days
    ).order_by('-start_time')[:20]
    
    # Get spectrum analysis data
    spectrum_data = SpectrumAnalysis.objects.filter(
        measurement_date__gte=last_7_days
    ).order_by('-measurement_date')[:10]
    
    # Generate trend data for charts
    trend_data = generate_trend_data(providers, last_7_days)
    
    # Regional QoS data
    regional_qos = get_regional_qos_data(today)
    
    context = {
        'providers': providers,
        'provider_data': provider_data,
        'active_incidents': active_incidents_list,
        'recent_incidents': recent_incidents,
        'spectrum_data': spectrum_data,
        'trend_data': json.dumps(trend_data),
        'regional_qos': regional_qos,
        'today': today,
    }
    
    return render(request, 'monitoring/dashboard.html', context)


def create_dummy_providers():
    """Create dummy data for demonstration"""
    providers = [
        {'name': 'Mascom', 'code': 'MAS', 'color': '#FF6B6B'},
        {'name': 'Orange', 'code': 'ORG', 'color': '#FFA500'},
        {'name': 'BTC', 'code': 'BTC', 'color': '#4ECDC4'},
    ]
    
    for p in providers:
        provider, created = TelecomProvider.objects.get_or_create(
            code=p['code'],
            defaults={
                'name': p['name'],
                'color': p['color'],
                'is_active': True
            }
        )
        
        # Create dummy metrics for last 7 days
        regions = ['gaborone', 'francistown', 'maun', 'kanye', 'serowe']
        services = ['voice', 'data', 'sms']
        
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            for region in regions:
                for service in services:
                    NetworkQualityMetrics.objects.create(
                        provider=provider,
                        service_type=service,
                        region=region,
                        date=date,
                        call_drop_rate=random.uniform(0.5, 3.0),
                        call_setup_success_rate=random.uniform(95, 99.5),
                        avg_throughput=random.uniform(10, 100),
                        latency=random.uniform(20, 100),
                        jitter=random.uniform(5, 30),
                        packet_loss=random.uniform(0.1, 2.0),
                        uptime_percentage=random.uniform(99.5, 99.99),
                        downtime_minutes=random.randint(0, 60),
                    )
        
        # Create dummy incidents
        NetworkIncident.objects.create(
            provider=provider,
            title="Network Degradation",
            incident_type="degraded",
            severity="medium",
            affected_services="Voice, Data",
            affected_regions="Gaborone, Francistown",
            description="Higher than normal packet loss reported",
            start_time=timezone.now() - timedelta(hours=3),
            is_resolved=False
        )
        
        # Create spectrum data
        SpectrumAnalysis.objects.create(
            provider=provider,
            frequency_band="2100MHz",
            measurement_date=timezone.now(),
            avg_power_dbm=random.uniform(-80, -40),
            peak_power_dbm=random.uniform(-70, -30),
            noise_floor=random.uniform(-100, -85),
            interference_detected=random.choice([True, False]),
            spectrum_snapshot={'frequencies': list(range(2100, 2200, 10)), 'power': [random.uniform(-90, -40) for _ in range(10)]}
        )


def generate_trend_data(providers, start_date):
    """Generate trend data for charts"""
    trend_data = []
    for provider in providers:
        metrics = NetworkQualityMetrics.objects.filter(
            provider=provider,
            date__gte=start_date
        ).values('date').annotate(
            avg_latency=Avg('latency'),
            avg_throughput=Avg('avg_throughput'),
            avg_uptime=Avg('uptime_percentage')
        ).order_by('date')
        
        trend_data.append({
            'provider': provider.name,
            'color': provider.color,
            'data': list(metrics)
        })
    
    return trend_data


def get_regional_qos_data(date):
    """Get regional QoS data for display"""
    regions = {}
    for region in NetworkQualityMetrics.REGIONS:
        metrics = NetworkQualityMetrics.objects.filter(
            region=region[0],
            date=date
        ).aggregate(
            avg_throughput=Avg('avg_throughput'),
            avg_latency=Avg('latency')
        )
        regions[region[1]] = {
            'throughput': round(metrics['avg_throughput'] or 0, 1),
            'latency': round(metrics['avg_latency'] or 0, 1)
        }
    
    return regions