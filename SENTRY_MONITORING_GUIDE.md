# Sentry Monitoring & Logging Guide

## Overview
This guide explains how to use the comprehensive Sentry monitoring system integrated into the nxtbn application. The system provides error tracking, performance monitoring, logging, and metrics collection.

## Table of Contents
1. [Configuration](#configuration)
2. [Testing the Setup](#testing-the-setup)
3. [Using Monitoring Utilities](#using-monitoring-utilities)
4. [Best Practices](#best-practices)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Sentry Configuration
SENTRY_ENVIRONMENT=production  # or development, staging
SENTRY_DEBUG_MODE=false  # Set to true to send events even in DEBUG mode

# Logging Level
DJANGO_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Sample Rates Explained

The configuration automatically adjusts based on your environment:

**Development (DEBUG=True):**
- `traces_sample_rate=1.0` - Captures 100% of transactions
- `profile_session_sample_rate=1.0` - Profiles 100% of sessions

**Production (DEBUG=False):**
- `traces_sample_rate=0.2` - Captures 20% of transactions (reduces overhead)
- `profile_session_sample_rate=0.1` - Profiles 10% of sessions

You can adjust these in `settings.py` based on your needs.

---

## Testing the Setup

### 1. Test Error Tracking

Visit the debug endpoint to trigger a test error:

```
http://localhost:8000/sentry-debug/
```

This will:
- Create a division by zero error
- Send the error to Sentry
- Show up in your Sentry dashboard

### 2. Check Health Status

Visit the health check endpoint:

```
http://localhost:8000/health/
```

This returns:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "environment": "development",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

### 3. Test Logging

In any view or function:

```python
import logging
logger = logging.getLogger('nxtbn')

logger.info('This is an info message')
logger.warning('This is a warning')
logger.error('This is an error - will be sent to Sentry')
```

---

## Using Monitoring Utilities

### Import the Utilities

```python
from nxtbn.core.monitoring import (
    log_info, log_warning, log_error,
    capture_exception, capture_message,
    track_performance, set_user_context,
    add_breadcrumb, track_metric
)
```

### 1. Logging

```python
# Info logging (console + breadcrumbs)
log_info('User viewed product page', extra={
    'product_id': product.id,
    'user_id': request.user.id
})

# Warning logging
log_warning('Low stock alert', extra={
    'product_id': product.id,
    'stock_level': product.stock
})

# Error logging (sent to Sentry)
log_error('Payment processing failed', extra={
    'order_id': order.id,
    'error_code': 'PAYMENT_DECLINED'
})
```

### 2. Exception Tracking

```python
try:
    # Your code here
    process_payment(order)
except PaymentError as e:
    capture_exception(e, context={
        'order_id': order.id,
        'payment_method': order.payment_method,
        'amount': order.total_amount
    })
    # Handle the error
```

### 3. Performance Tracking

#### Track Function Performance

```python
from nxtbn.core.monitoring import track_performance

@track_performance("order_processing")
def process_order(order_id):
    # This function's performance will be tracked
    order = Order.objects.get(id=order_id)
    # ... processing logic
    return order
```

#### Track Specific Operations

```python
from nxtbn.core.monitoring import start_span

def get_user_orders(user_id):
    with start_span("database.query", "Fetch user orders"):
        orders = Order.objects.filter(user_id=user_id).select_related('items')
    
    with start_span("serialization", "Serialize order data"):
        serialized = OrderSerializer(orders, many=True).data
    
    return serialized
```

### 4. User Context

Set user context for better error tracking:

```python
from nxtbn.core.monitoring import set_user_context

# In a view or middleware
def my_view(request):
    set_user_context(request.user)
    # Now all errors will include user information
```

### 5. Custom Context

Add custom context to errors:

```python
from nxtbn.core.monitoring import set_custom_context

set_custom_context("order_context", {
    "order_id": order.id,
    "total_amount": float(order.total_amount),
    "payment_status": order.payment_status
})
```

### 6. Breadcrumbs

Add breadcrumbs for debugging:

```python
from nxtbn.core.monitoring import add_breadcrumb

add_breadcrumb(
    message="User added item to cart",
    category="cart",
    level="info",
    data={
        "product_id": product.id,
        "quantity": quantity
    }
)
```

### 7. Metrics Tracking

Track business metrics:

```python
from nxtbn.core.monitoring import (
    increment_counter,
    record_distribution,
    set_gauge
)

# Count events
increment_counter("checkout.completed", tags={
    "payment_method": "hubtel"
})

# Track distributions (for averages, percentiles)
record_distribution(
    "cart.amount_usd",
    float(cart.total),
    unit="dollar",
    tags={"currency": cart.currency}
)

# Set current values
set_gauge(
    "inventory.stock_level",
    product.stock_quantity,
    unit="unit",
    tags={"product_id": str(product.id)}
)
```

### 8. Monitor Slow Database Queries

```python
from nxtbn.core.monitoring import monitor_slow_queries

@monitor_slow_queries(threshold_ms=500)  # Warn if takes > 500ms
def get_complex_report():
    # Complex database queries
    return Report.objects.select_related(...).prefetch_related(...)
```

---

## Best Practices

### 1. Use Appropriate Log Levels

- **INFO**: Normal operations (user actions, successful processes)
- **WARNING**: Unexpected but handled situations (low stock, deprecated features)
- **ERROR**: Errors that need attention (payment failures, API errors)

### 2. Add Context to Errors

Always include relevant context when capturing exceptions:

```python
try:
    process_payment(order)
except Exception as e:
    capture_exception(e, context={
        'order_id': order.id,
        'user_id': order.user_id,
        'amount': order.total_amount,
        'payment_gateway': 'hubtel'
    })
```

### 3. Track Key Business Metrics

```python
# Track important business events
increment_counter("order.created")
increment_counter("payment.success", tags={"method": "mobile_money"})
record_distribution("order.value", order.total_amount, unit="dollar")
```

### 4. Use Performance Tracking for Critical Paths

```python
@track_performance("checkout_flow")
def complete_checkout(cart_id):
    # Critical path - track performance
    pass
```

### 5. Set User Context Early

In middleware or authentication:

```python
class CustomAuthMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            set_user_context(request.user)
        return self.get_response(request)
```

---

## Production Deployment

### 1. Environment Configuration

Set these environment variables in production:

```env
DEBUG=false
SENTRY_ENVIRONMENT=production
DJANGO_LOG_LEVEL=WARNING  # Reduce noise in production
```

### 2. Add Request Monitoring Middleware

In `settings.py`, add to MIDDLEWARE:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'nxtbn.core.monitoring.SentryRequestMonitoringMiddleware',  # Add this
    # ... other middleware
]
```

### 3. Monitor Critical Operations

Add monitoring to critical business operations:

```python
# In order processing
from nxtbn.core.monitoring import track_performance, log_info, capture_exception

@track_performance("order_creation")
def create_order(cart):
    try:
        log_info('Creating order', extra={'cart_id': cart.id})
        order = Order.objects.create(...)
        increment_counter('order.created')
        return order
    except Exception as e:
        capture_exception(e, context={'cart_id': cart.id})
        raise
```

### 4. Set Up Alerts in Sentry

In your Sentry dashboard:
1. Go to **Alerts** → **Create Alert Rule**
2. Set up alerts for:
   - Error rate increases
   - Slow transaction detection
   - Failed health checks
   - Custom metric thresholds

---

## Troubleshooting

### Events Not Appearing in Sentry

1. **Check DSN**: Verify the DSN in `settings.py` is correct
2. **Check Environment**: If `DEBUG=True` and `SENTRY_DEBUG_MODE=False`, events won't be sent
3. **Check Network**: Ensure your server can reach Sentry's ingest endpoint
4. **Check Sample Rate**: In production, only 20% of transactions are sampled by default

### Health Check Failing

```bash
# Check database connectivity
python manage.py dbshell

# Check cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Too Many Events

If you're sending too many events to Sentry:

1. **Reduce Sample Rates** in `settings.py`:
   ```python
   traces_sample_rate=0.1  # Sample 10% instead of 20%
   ```

2. **Filter Errors** using `before_send`:
   ```python
   def before_send(event, hint):
       # Ignore certain errors
       if 'exc_info' in hint:
           exc_type, exc_value, tb = hint['exc_info']
           if isinstance(exc_value, SomeIgnorableError):
               return None
       return event
   
   sentry_sdk.init(
       # ...
       before_send=before_send
   )
   ```

3. **Add to ignore_errors**:
   ```python
   ignore_errors=[
       KeyboardInterrupt,
       BrokenPipeError,
       # Add other errors to ignore
   ]
   ```

---

## Example: Complete Order Processing with Monitoring

```python
from nxtbn.core.monitoring import (
    track_performance,
    log_info,
    log_error,
    capture_exception,
    add_breadcrumb,
    increment_counter,
    record_distribution,
    set_custom_context
)

@track_performance("order_processing")
def process_order(order_id):
    try:
        # Set context
        set_custom_context("order", {"order_id": order_id})
        
        # Add breadcrumb
        add_breadcrumb(
            message="Starting order processing",
            category="order",
            data={"order_id": order_id}
        )
        
        # Get order
        order = Order.objects.get(id=order_id)
        log_info(f"Processing order {order_id}", extra={
            "order_id": order_id,
            "total": float(order.total_amount)
        })
        
        # Process payment
        add_breadcrumb(message="Processing payment", category="payment")
        payment_result = process_payment(order)
        
        if payment_result.success:
            # Track success
            increment_counter("order.payment.success", tags={
                "payment_method": order.payment_method
            })
            record_distribution(
                "order.amount",
                float(order.total_amount),
                unit="dollar"
            )
            
            log_info(f"Order {order_id} completed successfully")
            return order
        else:
            # Track failure
            increment_counter("order.payment.failed", tags={
                "payment_method": order.payment_method,
                "reason": payment_result.error_code
            })
            log_error(f"Payment failed for order {order_id}", extra={
                "error_code": payment_result.error_code
            })
            raise PaymentError(payment_result.error_message)
            
    except Exception as e:
        # Capture exception with full context
        capture_exception(e, context={
            "order_id": order_id,
            "step": "order_processing"
        })
        raise
```

---

## Additional Resources

- [Sentry Django Documentation](https://docs.sentry.io/platforms/python/guides/django/)
- [Sentry Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Sentry Metrics](https://docs.sentry.io/product/metrics/)
- [Best Practices for Error Tracking](https://docs.sentry.io/product/issues/issue-details/)

---

## Quick Reference

### Common Imports
```python
from nxtbn.core.monitoring import (
    log_info, log_warning, log_error,
    capture_exception, track_performance,
    increment_counter, record_distribution
)
```

### Quick Examples
```python
# Log
log_info("User action", extra={"user_id": 123})

# Track exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={"operation": "risky"})

# Track performance
@track_performance("my_operation")
def my_function():
    pass

# Track metric
increment_counter("event.happened")
```
