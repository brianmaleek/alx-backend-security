from alx_backend_security.celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    """
    Hourly task to detect suspicious IP addresses
    """
    # Calculate time range (last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Get all requests from the last hour
    recent_requests = RequestLog.objects.filter(timestamp__gte=one_hour_ago)
    
    # 1. Check for IPs with excessive requests (>100/hour)
    high_volume_ips = recent_requests.values('ip_address').annotate(
        request_count=Count('id')
    ).filter(request_count__gt=100)
    
    for ip_data in high_volume_ips:
        ip_address = ip_data['ip_address']
        request_count = ip_data['request_count']
        reason = f"High volume: {request_count} requests in the last hour"
        
        SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={'reason': reason}
        )
    
    # 2. Check for IPs accessing sensitive paths
    sensitive_paths = ['/admin', '/login', '/admin/', '/login/']
    sensitive_requests = recent_requests.filter(path__in=sensitive_paths)
    
    # Group by IP and count sensitive path accesses
    sensitive_ip_counts = sensitive_requests.values('ip_address').annotate(
        sensitive_count=Count('id')
    ).filter(sensitive_count__gt=5)  # Flag if more than 5 sensitive requests
    
    for ip_data in sensitive_ip_counts:
        ip_address = ip_data['ip_address']
        sensitive_count = ip_data['sensitive_count']
        reason = f"Sensitive path access: {sensitive_count} attempts to sensitive endpoints"
        
        SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={'reason': reason}
        )
    
    # 3. Check for rapid successive requests (potential brute force)
    rapid_requests = recent_requests.values('ip_address').annotate(
        request_count=Count('id')
    ).filter(request_count__gt=50)  # More than 50 requests in an hour
    
    for ip_data in rapid_requests:
        ip_address = ip_data['ip_address']
        request_count = ip_data['request_count']
        reason = f"Rapid requests: {request_count} requests in the last hour"
        
        SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={'reason': reason}
        )
    
    return f"Anomaly detection completed. Found {len(high_volume_ips) + len(sensitive_ip_counts) + len(rapid_requests)} suspicious IPs"

@shared_task
def cleanup_old_suspicious_ips():
    """
    Clean up old suspicious IP records (older than 7 days)
    """
    seven_days_ago = timezone.now() - timedelta(days=7)
    deleted_count = SuspiciousIP.objects.filter(
        created_at__lt=seven_days_ago,
        is_active=False
    ).delete()[0]
    
    return f"Cleaned up {deleted_count} old suspicious IP records" 