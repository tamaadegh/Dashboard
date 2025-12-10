from django.urls import include, path
from rest_framework.routers import DefaultRouter
from nxtbn.shipping.api.dashboard.views import (
    CustomerEligibleShippingMethodstAPI, 
    ShippingMethodDetails,
    ShippingMethodTranslationViewSet,
    ShippingRateListCreateView,
    ShippingRateDetailView, 
    ShippingMethodstListAPI
)

router = DefaultRouter()
router.register(r'shipping-method-translations', ShippingMethodTranslationViewSet, basename='shipping-method-translation')


urlpatterns = [
    path('', include(router.urls)),
    path('customer/eligible-shipping-method/', CustomerEligibleShippingMethodstAPI.as_view(), name='customer-shipping-methods'),
    path('shipping-methods/', ShippingMethodstListAPI.as_view(), name='customer-shipping-method-list'),
    path('shipping-method/<int:id>/', ShippingMethodDetails.as_view(), name='customer-shipping-method-detail'),

    path('shipping-rates/', ShippingRateListCreateView.as_view(), name='shipping-rate-view'),
    path('shipping-rates/<int:id>/', ShippingRateDetailView.as_view(), name='shipping-rate-detail-view'),

]
