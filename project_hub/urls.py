from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_hub.urls')),

    # SEO files at root for Google
    path('favicon.ico', TemplateView.as_view(
        template_name='img/favicon.ico', content_type='image/x-icon')),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml', content_type='application/xml')),
]

# Serve media files in production (bypasses DEBUG check)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
]
