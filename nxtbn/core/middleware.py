"""
Custom Middleware for Request Monitoring

Add this to your MIDDLEWARE in settings.py:
    'nxtbn.core.middleware.RequestMonitoringMiddleware',
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from nxtbn.core.monitoring import (
    set_user_context,
    add_breadcrumb,
    record_distribution,
    set_custom_context,
    log_warning,
)

logger = logging.getLogger('nxtbn')


class RequestMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to automatically monitor all requests with Sentry
    """
    
    def process_request(self, request):
        """Called before Django decides which view to execute"""
        # Store start time
        request._monitoring_start_time = time.time()
        
        # Set user context if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_user_context(request.user)
        
        # Add request breadcrumb
        add_breadcrumb(
            message=f"{request.method} {request.path}",
            category="request",
            level="info",
            data={
                "method": request.method,
                "path": request.path,
                "query_string": request.META.get('QUERY_STRING', ''),
            }
        )
        
        # Set request context
        set_custom_context("request", {
            "method": request.method,
            "path": request.path,
            "user_agent": request.META.get('HTTP_USER_AGENT', '')[:200],
            "ip_address": self._get_client_ip(request),
        })
        
        return None
    
    def process_response(self, request, response):
        """Called after the view returns a response"""
        # Calculate request duration
        if hasattr(request, '_monitoring_start_time'):
            duration_ms = (time.time() - request._monitoring_start_time) * 1000
            
            # Get route pattern if available
            route = 'unknown'
            if hasattr(request, 'resolver_match') and request.resolver_match:
                route = request.resolver_match.route or 'unknown'
            
            # Track request duration (tags not supported in current SDK)
            record_distribution(
                "http.request.duration",
                duration_ms,
                unit="millisecond"
            )
            
            # Log slow requests (> 2 seconds)
            if duration_ms > 2000:
                log_warning(
                    f"Slow request detected: {request.method} {request.path}",
                    extra={
                        'duration_ms': duration_ms,
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                    }
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Called when a view raises an exception"""
        from nxtbn.core.monitoring import capture_exception
        
        # Capture the exception with request context
        capture_exception(exception, context={
            'request_method': request.method,
            'request_path': request.path,
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
        })
        
        # Return None to let Django handle the exception normally
        return None
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
