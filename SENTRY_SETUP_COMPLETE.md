# Sentry Monitoring Setup - Quick Start

## ✅ What's Been Configured

Your Django application now has comprehensive Sentry monitoring with:

### 1. **Enhanced Sentry Configuration** (`settings.py`)
- ✅ Environment-based configuration (development/production)
- ✅ Release tracking with version numbers
- ✅ Optimized sample rates (20% in production, 100% in development)
- ✅ Comprehensive logging configuration
- ✅ Automatic error and performance tracking

### 2. **Monitoring Endpoints** (`urls.py`)
- ✅ `/sentry-debug/` - Test error tracking
- ✅ `/health/` - Application health check

### 3. **Monitoring Utilities** (`nxtbn/core/monitoring.py`)
Complete toolkit for:
- Logging (info, warning, error)
- Exception tracking
- Performance monitoring
- Metrics collection
- User context management
- Breadcrumbs for debugging

### 4. **Automatic Request Monitoring** (`nxtbn/core/middleware.py`)
- ✅ Tracks all HTTP requests
- ✅ Monitors request duration
- ✅ Logs slow requests (> 2 seconds)
- ✅ Captures exceptions automatically
- ✅ Sets user context

### 5. **Example Implementation** (`hubtel_payments/views_with_monitoring_example.py`)
Reference implementation showing how to add monitoring to payment processing

---

## 🚀 Quick Test

### 1. Restart Your Development Server

The server is already running. Restart it to load the new middleware:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### 2. Test Error Tracking

Visit: http://localhost:8000/sentry-debug/

This will:
- Trigger a test error
- Send it to Sentry
- Appear in your Sentry dashboard at: https://o4510818177056768.ingest.de.sentry.io/

### 3. Check Health Status

Visit: http://localhost:8000/health/

Should return:
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

### 4. View in Sentry Dashboard

1. Go to: https://sentry.io/organizations/your-org/issues/
2. You should see the test error from `/sentry-debug/`
3. Click on it to see:
   - Full stack trace
   - Request information
   - User context
   - Breadcrumbs

---

## 📊 What You'll See in Production

When deployed to production, Sentry will automatically track:

### **Errors**
- Unhandled exceptions
- Database errors
- API failures
- Payment processing errors

### **Performance**
- Slow database queries
- API response times
- Request duration
- Transaction traces

### **Metrics**
- Request counts
- Error rates
- Payment success/failure rates
- Custom business metrics

### **Context**
- User information
- Request details
- Custom context data
- Breadcrumbs showing user actions

---

## 🔧 Environment Variables

Add these to your production `.env`:

```env
# Sentry Configuration
SENTRY_ENVIRONMENT=production
DJANGO_LOG_LEVEL=WARNING

# Optional: Enable Sentry in DEBUG mode (for testing)
SENTRY_DEBUG_MODE=false
```

---

## 📝 How to Use in Your Code

### Basic Logging

```python
from nxtbn.core.monitoring import log_info, log_warning, log_error

# Info (console + breadcrumbs)
log_info('User viewed product', extra={'product_id': 123})

# Warning
log_warning('Low stock', extra={'product_id': 123, 'stock': 5})

# Error (sent to Sentry)
log_error('Payment failed', extra={'order_id': 456})
```

### Track Exceptions

```python
from nxtbn.core.monitoring import capture_exception

try:
    process_payment(order)
except PaymentError as e:
    capture_exception(e, context={
        'order_id': order.id,
        'amount': order.total
    })
```

### Track Performance

```python
from nxtbn.core.monitoring import track_performance

@track_performance("order_processing")
def process_order(order_id):
    # Your code here
    pass
```

### Track Metrics

```python
from nxtbn.core.monitoring import increment_counter, record_distribution

# Count events
increment_counter('order.created')

# Track values
record_distribution('order.amount', order.total, unit='dollar')
```

---

## 🎯 Next Steps

### 1. **Test the Setup**
- Visit `/sentry-debug/` to trigger a test error
- Check your Sentry dashboard
- Visit `/health/` to verify health checks

### 2. **Add Monitoring to Critical Paths**
Use the example in `hubtel_payments/views_with_monitoring_example.py` as a reference to add monitoring to:
- Payment processing
- Order creation
- User authentication
- API endpoints

### 3. **Set Up Alerts in Sentry**
1. Go to Sentry → Alerts → Create Alert Rule
2. Set up alerts for:
   - Error rate increases
   - Slow transactions
   - Failed payments
   - Health check failures

### 4. **Monitor Production Issues**

When you see "URL cannot be reached" in production:

1. **Check Sentry Dashboard** for:
   - Recent errors
   - Performance issues
   - Failed requests

2. **Check Health Endpoint**:
   ```bash
   curl https://your-domain.com/health/
   ```

3. **Review Logs** in Sentry for:
   - Database connection errors
   - Memory issues
   - Timeout errors

---

## 📚 Documentation

- **Full Guide**: See `SENTRY_MONITORING_GUIDE.md`
- **Example Code**: See `hubtel_payments/views_with_monitoring_example.py`
- **Sentry Docs**: https://docs.sentry.io/platforms/python/guides/django/

---

## 🐛 Troubleshooting

### Events Not Showing in Sentry?

1. Check DSN is correct in `settings.py`
2. Ensure `DEBUG=False` or `SENTRY_DEBUG_MODE=True`
3. Check network connectivity to Sentry

### Too Many Events?

Reduce sample rates in `settings.py`:
```python
traces_sample_rate=0.1  # 10% instead of 20%
```

### Health Check Failing?

```bash
# Test database
python manage.py dbshell

# Test cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'ok')
>>> cache.get('test')
```

---

## 🎉 You're All Set!

Your application now has enterprise-grade monitoring. When production issues occur:

1. **Check Sentry** for errors and performance issues
2. **Use `/health/`** to verify service status
3. **Review breadcrumbs** to understand user actions leading to errors
4. **Track metrics** to identify patterns

The monitoring is automatic - no code changes needed for basic tracking!
