from django.urls import include, path
from nxtbn.discount.api.dashboard import views as discount_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),
    path('promocodes/', discount_views.PromoCodeListCreateAPIView.as_view(), name='promo-code-list-create'),
    path('promocodes/<int:id>/', discount_views.PromoCodeUpdateRetrieveDeleteView.as_view(), name='promo-code-update-delete'),
    path('promocodes/attach-entities/', discount_views.AttachPromoCodeEntitiesAPIView.as_view(), name='attach-promo-code-entities'),
    path('promocodes/products/', discount_views.PromoCodeProductListAPIView.as_view(), name='promo-code-product-list'),
    path('promocodes/customers/', discount_views.PromoCodeCustomertListAPIView.as_view(), name='promo-code-customer-list'),
    path('promocodes/usage/', discount_views.PromoCodeUsageListAPIView.as_view(), name='promo-code-usage-list'),
]
