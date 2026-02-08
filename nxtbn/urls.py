"""nxtbn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
import importlib
import sys
from django.http import HttpResponse
from django.conf import settings
from django.urls import re_path, path, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework.permissions import IsAdminUser

from nxtbn.admin_schema import admin_schema
from nxtbn.storefront_schema import storefront_schema
from nxtbn.swagger_views import DASHBOARD_API_DOCS_SCHEMA_VIEWS, STOREFRONT_API_DOCS_SCHEMA_VIEWS, api_docs



# showing exact error in remote development server
if getattr(settings, 'DEVELOPMENT_SERVER') and not getattr(settings, 'DEBUG'):
    ''' Response very short details error during staging server and when debug=False '''
    def short_technical_response(request, exc_type, exc_value, tb, status_code=500):
        return HttpResponse(exc_value, status=status_code)

    def handler500(request):
        return short_technical_response(request, *sys.exc_info())


# Admin placeholder change
admin.site.site_header = "Tamaade Administration"
admin.site.site_title = "Tamaade Admin Panel"
admin.site.index_title = "Tamaade Admin"

# Sentry monitoring endpoints
def trigger_error(request):
    """Endpoint to test Sentry error tracking"""
    import logging
    logger = logging.getLogger('nxtbn')
    logger.info('Sentry debug endpoint accessed')
    division_by_zero = 1 / 0  # This will trigger an error
    return HttpResponse("This should never be reached")

def health_check(request):
    """Health check endpoint for monitoring"""
    import json
    from django.db import connection
    from django.core.cache import cache
    import logging
    
    logger = logging.getLogger('nxtbn')
    health_status = {
        'status': 'healthy',
        'version': settings.VERSION,
        'environment': getattr(settings, 'SENTRY_ENVIRONMENT', 'unknown'),
        'checks': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
        logger.error(f'Database health check failed: {str(e)}')
    
    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        health_status['checks']['cache'] = 'ok' if cache_value == 'ok' else 'degraded'
    except Exception as e:
        health_status['checks']['cache'] = f'error: {str(e)}'
        logger.warning(f'Cache health check failed: {str(e)}')
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return HttpResponse(
        json.dumps(health_status, indent=2),
        content_type='application/json',
        status=status_code
    )

urlpatterns = [
    # Monitoring endpoints
    path('sentry-debug/', trigger_error, name='sentry_debug'),
    path('health/', health_check, name='health_check'),
    
    path('django-admin/', admin.site.urls),
    path('', include('nxtbn.home.urls')),
    path('', include('nxtbn.seo.urls')),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=storefront_schema))),
    path('admin-graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=admin_schema))),

    path('product/', include('nxtbn.product.urls')),

    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', TemplateView.as_view(template_name='account/profile.html'), name='account_profiles'),


    # API
    path('user/storefront/api/', include('nxtbn.users.api.storefront.urls')),
    path('user/dashboard/api/', include('nxtbn.users.api.dashboard.urls')),

    path('core/storefront/api/', include('nxtbn.core.api.storefront.urls')),
    path('core/dashboard/api/', include('nxtbn.core.api.dashboard.urls')),

    path('invoice/storefront/api/', include('nxtbn.invoice.api.storefront.urls')),
    path('invoice/dashboard/api/', include('nxtbn.invoice.api.dashboard.urls')),

    path('filemanager/storefront/api/', include('nxtbn.filemanager.api.storefront.urls')),
    path('filemanager/dashboard/api/', include('nxtbn.filemanager.api.dashboard.urls')),

    path('order/storefront/api/', include('nxtbn.order.api.storefront.urls')),
    path('order/dashboard/api/', include('nxtbn.order.api.dashboard.urls')),

    path('product/storefront/api/', include('nxtbn.product.api.storefront.urls')),
    path('product/dashboard/api/', include('nxtbn.product.api.dashboard.urls')),

    path('cart/dashboard/api/', include('nxtbn.cart.api.dashboard.urls')),

    # payment app replaced by Hubtel direct integration; keep hubtel endpoints below
    # Hubtel payment endpoints (storefront / mobile-app integration)
    path('payments/api/', include('nxtbn.hubtel_payments.urls')),

    path('seo/storefront/api/', include('nxtbn.seo.api.storefront.urls')),
    path('seo/dashboard/api/', include('nxtbn.seo.api.dashboard.urls')),

    path('core/storefront/api/', include('nxtbn.core.api.storefront.urls')),
    path('core/dashboard/api/', include('nxtbn.core.api.dashboard.urls')),

    path('shipping/dashboard/api/', include('nxtbn.shipping.api.dashboard.urls')),

    path('plugins/dashboard/api/', include('nxtbn.plugins.api.dashboard.urls')),

    path('discount/dashboard/api/', include('nxtbn.discount.api.dashboard.urls')),

    path('tax/dashboard/api/', include('nxtbn.tax.api.dashboard.urls')),

    path('warehouse/dashboard/api/', include('nxtbn.warehouse.api.dashboard.urls')),

    path('purchase/dashboard/api/', include('nxtbn.purchase.api.dashboard.urls')),

]

urlpatterns += [
    path('docs/', api_docs, name='api_docs'),
    path("docs-dashboard-swagger/", DASHBOARD_API_DOCS_SCHEMA_VIEWS.with_ui("swagger", cache_timeout=0), name="docs_dashboard_swagger"),
    path("docs-storefront-swagger/", STOREFRONT_API_DOCS_SCHEMA_VIEWS.with_ui("swagger", cache_timeout=0), name="docs_storefront_swagger"),

    path("docs-dashboard-redoc/", DASHBOARD_API_DOCS_SCHEMA_VIEWS.with_ui("redoc", cache_timeout=0), name="docs_dashboard_redoc"),
    path("docs-storefront-redoc/", STOREFRONT_API_DOCS_SCHEMA_VIEWS.with_ui("redoc", cache_timeout=0), name="docs_storefront_redoc")
]