from django.urls import path
from nxtbn.plugins.api.dashboard import views as plugins_views

urlpatterns = [
    path('pluggin-list/', plugins_views.PluginListView.as_view(), name='plugin-list'),
]
