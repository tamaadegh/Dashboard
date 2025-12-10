from django.urls import include, path
from nxtbn.users.api.dashboard import views as users_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', users_views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', users_views.DashboardLogoutView.as_view(), name='logout-dashboard'),
    path('customers/', users_views.CustomerListAPIView.as_view(), name='customer-list'),
    path('customers/<int:id>/', users_views.CustomerRetrieveUpdateAPIView.as_view(), name='customer-update'),
    path('customer-with-address/<int:id>/', users_views.CustomerWithAddressView.as_view(), name='customer-with-address'),
    path('change-password/', users_views.PasswordChangeView.as_view(), name='change_password'),
    path('address/', users_views.AddressCreateAPIView.as_view(), name='address-view'),
    path('address/<int:id>/', users_views.AddressRetriveUpdateDestroyAPIView.as_view(), name='address-view'),
    path('me/', users_views.MeDetailsAPIView.as_view(), name='me'),

]
