from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from .decorators import adaptive_rate_limit

# Create your views here.

@adaptive_rate_limit(authenticated_rate='10/m', anonymous_rate='5/m')
@csrf_exempt
def login_view(request):
    """Sensitive login view with adaptive rate limiting"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success', 'message': 'Login successful'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
        else:
            return JsonResponse({'status': 'error', 'message': 'Missing credentials'}, status=400)
    
    return render(request, 'ip_tracking/login.html')

@adaptive_rate_limit(authenticated_rate='20/m', anonymous_rate='5/m')
def api_endpoint(request):
    """API endpoint with different limits for authenticated vs anonymous users"""
    return JsonResponse({'status': 'success', 'message': 'API response'})
