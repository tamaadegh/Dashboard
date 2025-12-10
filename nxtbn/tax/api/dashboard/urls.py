from django.urls import include, path
from rest_framework.routers import DefaultRouter
from nxtbn.tax.api.dashboard.views import (
    TaxClassView, 
    TaxClassDetailsView, 
    TaxRateListCreateAPIView, 
    TaxRateRetrieveUpdateDelete
)

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('tax-class/', TaxClassView.as_view(), name='tax-class-list-create'),
    path('tax-class/<int:id>/', TaxClassDetailsView.as_view(), name='tax-class-detail'),
    path('tax-rates/', TaxRateListCreateAPIView.as_view(), name='tax-rates-by-tax-class'),
    path('tax-rates/<int:id>/', TaxRateRetrieveUpdateDelete.as_view(), name='tax-rates-retrieve-update-delete')

]
