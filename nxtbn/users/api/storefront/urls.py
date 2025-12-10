from django.urls import path

from nxtbn.users.api.storefront.views import SignupView, LogoutView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='customer_signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
