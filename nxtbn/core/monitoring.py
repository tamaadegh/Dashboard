"""
Sentry Monitoring Utilities for nxtbn

This module provides utilities for comprehensive application monitoring,
logging, and performance tracking using Sentry.

Usage:
    from nxtbn.core.monitoring import (
        log_info, log_warning, log_error,
        capture_exception, capture_message,
        track_performance, set_user_context
    )
"""

import logging
import sentry_sdk
from functools import wraps
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger('nxtbn')


# ============================
# Logging Utilities
# ============================

def log_info(message: str, extra: Optional[Dict[str, Any]] = None):
    """
    Log an info message to console and Sentry breadcrumbs
    
    Args:
        message: The log message
        extra: Additional context data
    """
    logger.info(message, extra=extra or {})
    sentry_sdk.add_breadcrumb(
        category='info',
        message=message,
        level='info',
        data=extra or {}
    )


def log_warning(message: str, extra: Optional[Dict[str, Any]] = None):
    """
    Log a warning message
    
    Args:
        message: The warning message
        extra: Additional context data
    """
    logger.warning(message, extra=extra or {})
    sentry_sdk.add_breadcrumb(
        category='warning',
        message=message,
        level='warning',
        data=extra or {}
    )


def log_error(message: str, extra: Optional[Dict[str, Any]] = None):
    """
    Log an error message and send to Sentry
    
    Args:
        message: The error message
        extra: Additional context data
    """
    logger.error(message, extra=extra or {})
    sentry_sdk.capture_message(message, level='error', extras=extra or {})


# ============================
# Exception Tracking
# ============================

def capture_exception(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: str = 'error'
):
    """
    Capture an exception and send to Sentry with additional context
    
    Args:
        exception: The exception to capture
        context: Additional context data
        level: Severity level (error, warning, info)
    """
    if context:
        sentry_sdk.set_context("custom", context)
    
    sentry_sdk.capture_exception(exception, level=level)
    logger.exception(f"Exception captured: {str(exception)}", extra=context or {})


def capture_message(
    message: str,
    level: str = 'info',
    extras: Optional[Dict[str, Any]] = None
):
    """
    Capture a message and send to Sentry
    
    Args:
        message: The message to capture
        level: Severity level
        extras: Additional data
    """
    sentry_sdk.capture_message(message, level=level, extras=extras or {})


# ============================
# Performance Tracking
# ============================

def track_performance(operation_name: str):
    """
    Decorator to track performance of a function
    
    Usage:
        @track_performance("process_order")
        def process_order(order_id):
            # Your code here
            pass
    
    Args:
        operation_name: Name of the operation being tracked
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_transaction(
                op=operation_name,
                name=f"{func.__module__}.{func.__name__}"
            ) as transaction:
                try:
                    result = func(*args, **kwargs)
                    transaction.set_status("ok")
                    return result
                except Exception as e:
                    transaction.set_status("internal_error")
                    capture_exception(e, context={
                        'operation': operation_name,
                        'function': func.__name__,
                        'args': str(args)[:200],  # Limit size
                        'kwargs': str(kwargs)[:200]
                    })
                    raise
        return wrapper
    return decorator


def start_span(operation: str, description: Optional[str] = None):
    """
    Start a performance span for detailed tracking
    
    Usage:
        with start_span("database.query", "Fetch user orders"):
            # Your database query here
            pass
    
    Args:
        operation: Type of operation (e.g., "database.query", "http.request")
        description: Human-readable description
    """
    return sentry_sdk.start_span(op=operation, description=description)


# ============================
# Context Management
# ============================

def set_user_context(user):
    """
    Set user context for Sentry tracking
    
    Args:
        user: Django User object
    """
    if user and user.is_authenticated:
        sentry_sdk.set_user({
            "id": user.id,
            "email": user.email,
            "username": getattr(user, 'username', None),
        })
    else:
        sentry_sdk.set_user(None)


def set_custom_context(key: str, data: Dict[str, Any]):
    """
    Set custom context data for Sentry
    
    Args:
        key: Context key
        data: Context data dictionary
    """
    sentry_sdk.set_context(key, data)


def add_breadcrumb(
    message: str,
    category: str = 'custom',
    level: str = 'info',
    data: Optional[Dict[str, Any]] = None
):
    """
    Add a breadcrumb for debugging
    
    Args:
        message: Breadcrumb message
        category: Category (e.g., 'auth', 'query', 'navigation')
        level: Severity level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level,
        data=data or {}
    )


# ============================
# Metrics Tracking
# ============================

def track_metric(metric_name: str, value: float, unit: str = "none", tags: Optional[Dict[str, str]] = None):
    """
    Track a custom metric in Sentry
    
    Args:
        metric_name: Name of the metric (e.g., "checkout.failed", "cart.amount_usd")
        value: Metric value
        unit: Unit of measurement
        tags: Additional tags for filtering (not supported in current SDK version)
    """
    from sentry_sdk import metrics
    
    # Note: tags parameter not supported in current Sentry SDK version
    if metric_name.endswith('.count'):
        metrics.incr(metric_name, value=int(value))
    elif metric_name.endswith('.gauge'):
        metrics.gauge(metric_name, value=value, unit=unit)
    else:
        metrics.distribution(metric_name, value=value, unit=unit)


def increment_counter(metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """
    Increment a counter metric
    
    Args:
        metric_name: Name of the counter
        value: Amount to increment
        tags: Additional tags (not supported in current SDK version)
    """
    from sentry_sdk import metrics
    # Note: tags parameter not supported in current Sentry SDK version
    metrics.incr(metric_name, value=value)


def record_distribution(metric_name: str, value: float, unit: str = "none", tags: Optional[Dict[str, str]] = None):
    """
    Record a distribution metric (for percentiles, averages, etc.)
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        tags: Additional tags (not supported in current SDK version)
    """
    from sentry_sdk import metrics
    # Note: tags parameter not supported in current Sentry SDK version
    metrics.distribution(metric_name, value=value, unit=unit)


def set_gauge(metric_name: str, value: float, unit: str = "none", tags: Optional[Dict[str, str]] = None):
    """
    Set a gauge metric (current value)
    
    Args:
        metric_name: Name of the gauge
        value: Current value
        unit: Unit of measurement
        tags: Additional tags (not supported in current SDK version)
    """
    from sentry_sdk import metrics
    # Note: tags parameter not supported in current Sentry SDK version
    metrics.gauge(metric_name, value=value, unit=unit)


# ============================
# Database Query Monitoring
# ============================

def monitor_slow_queries(threshold_ms: int = 1000):
    """
    Decorator to monitor and log slow database queries
    
    Args:
        threshold_ms: Threshold in milliseconds for slow query warning
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from django.db import connection, reset_queries
            from django.conf import settings
            
            # Enable query logging temporarily
            old_debug = settings.DEBUG
            settings.DEBUG = True
            reset_queries()
            
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = (time.time() - start_time) * 1000
                query_count = len(connection.queries)
                
                if duration_ms > threshold_ms:
                    log_warning(
                        f"Slow operation detected: {func.__name__}",
                        extra={
                            'duration_ms': duration_ms,
                            'query_count': query_count,
                            'function': func.__name__
                        }
                    )
                
                # Track metrics (tags not supported in current SDK)
                record_distribution(
                    f"database.query.duration",
                    duration_ms,
                    unit="millisecond"
                )
                
                return result
            finally:
                settings.DEBUG = old_debug
        
        return wrapper
    return decorator


# ============================
# Request Monitoring Middleware
# ============================

class SentryRequestMonitoringMiddleware:
    """
    Middleware to add request context and monitor request performance
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set request context
        sentry_sdk.set_context("request_info", {
            "path": request.path,
            "method": request.method,
            "user_agent": request.META.get('HTTP_USER_AGENT', ''),
        })
        
        # Track user if authenticated
        if hasattr(request, 'user'):
            set_user_context(request.user)
        
        # Add breadcrumb
        add_breadcrumb(
            message=f"{request.method} {request.path}",
            category="request",
            level="info"
        )
        
        # Process request
        import time
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Track request duration
        duration_ms = (time.time() - start_time) * 1000
        record_distribution(
            "http.request.duration",
            duration_ms,
            unit="millisecond",
            tags={
                'method': request.method,
                'status': response.status_code,
                'path_template': getattr(request.resolver_match, 'route', 'unknown') if hasattr(request, 'resolver_match') else 'unknown'
            }
        )
        
        return response
