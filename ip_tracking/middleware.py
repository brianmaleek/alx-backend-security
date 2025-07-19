from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
from django.utils.deprecation import MiddlewareMixin
import json

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        
        # Block if IP is blacklisted
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")
        
        path = request.path
        
        # Get geolocation data (cached for 24 hours)
        country, city = self.get_geolocation_data(ip)
        
        # Create log entry
        RequestLog.objects.create(
            ip_address=ip,
            path=path,
            country=country,
            city=city
        )
    
    def get_client_ip(self, request):
        try:
            from ipware import get_client_ip
            ip, _ = get_client_ip(request)
            if ip:
                return ip
        except ImportError:
            pass
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def get_geolocation_data(self, ip):
        cache_key = f"geo_{ip}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data.get('country'), cached_data.get('city')
        
        try:
            import geoip2.database
            # Download GeoLite2-City.mmdb from MaxMind
            reader = geoip2.database.Reader('GeoLite2-City.mmdb')
            response = reader.city(ip)
            
            country = response.country.name or ''
            city = response.city.name or ''
            
            cache_data = {'country': country, 'city': city}
            cache.set(cache_key, cache_data, 86400)
            
            return country, city
        except Exception as e:
            print(f"Geolocation error for IP {ip}: {e}")
        
        return '', ''
