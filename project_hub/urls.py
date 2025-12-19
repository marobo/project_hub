from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_hub.urls')),

    # Root favicon redirect for Google/browsers that look for /favicon.ico
    path('favicon.ico', RedirectView.as_view(
        url='/static/img/favicon.ico', permanent=True)),
]

# Serve media files in production (bypasses DEBUG check)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
]
