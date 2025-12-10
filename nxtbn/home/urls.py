from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

from nxtbn.home import views as home_views


urlpatterns = [
    path('', home_views.home, name='home'),
    # re_path(r'^dashboard(?:/.*)?$', home_views.nxtbn_dashboard, name='nxtbn_dashboard'),
    re_path(r'^dashboard(/.*)?$', home_views.nxtbn_dashboard, name='nxtbn_dashboard'),
    path('upload-admin/', home_views.upload_admin, name='upload_admin'),
    path('get-help/', home_views.get_help, name='get_help'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)