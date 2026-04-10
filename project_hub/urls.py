from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve


def _root_static_document_root():
    """Source `static/` in dev; `collectstatic` output when DEBUG is False."""
    if settings.DEBUG:
        return settings.STATICFILES_DIRS[0]
    return settings.STATIC_ROOT


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_hub.urls')),
    path('growth/', include('django_growth.urls')),

    # SEO files at site root (STATIC_ROOT after collectstatic in production)
    path('favicon.ico', serve, {
        'document_root': _root_static_document_root(),
        'path': 'img/favicon.ico',
    }),
    path('robots.txt', serve, {
        'document_root': _root_static_document_root(),
        'path': 'robots.txt',
    }),
    path('sitemap.xml', serve, {
        'document_root': _root_static_document_root(),
        'path': 'sitemap.xml',
    }),
]

# Serve media files in production (bypasses DEBUG check)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
]
