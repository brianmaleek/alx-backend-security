from django_ratelimit.decorators import ratelimit
from functools import wraps

def adaptive_rate_limit(authenticated_rate='10/m', anonymous_rate='5/m'):
    """
    Custom decorator that applies different rate limits based on authentication status
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Determine rate limit based on authentication
            if request.user.is_authenticated:
                rate = authenticated_rate
                key = f"user_{request.user.id}"
            else:
                rate = anonymous_rate
                key = f"ip_{request.META.get('REMOTE_ADDR', 'unknown')}"
            
            # Apply rate limit
            return ratelimit(key=key, rate=rate, method='POST', block=True)(view_func)(request, *args, **kwargs)
        return wrapped_view
    return decorator
