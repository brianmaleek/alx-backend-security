from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        # Block specific IPs
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")
        path = request.path
        RequestLog.objects.create(ip_address=ip, path=path)
    
    def get_client_ip(self, request):
        # Use django-ipware if installed, else fallback
        try:
            from ipware import get_client_ip
            ip, _ = get_client_ip(request)
            if ip:
                return ip
        except ImportError:
            pass
        # Fallback to META
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
