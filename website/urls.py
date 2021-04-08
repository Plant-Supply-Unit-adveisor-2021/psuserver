"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from website.securemedia import psufeed_handler

# URL Patterns without i18n tags
urlpatterns = [
    path(r'psucontrol/', include('psucontrol.urls', namespace='psucontrol')),
    path(r'securemedia/', include('website.securemedia', namespace='securemedia'))
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static('protectedmedia', document_root=settings.SECURE_MEDIA_ROOT)

# DEBUG -> add urls for serving static files
if settings.DEBUG:
    # media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # protected files via securemedia
    urlpatterns += static('protectedmedia', document_root=settings.SECURE_MEDIA_ROOT)

# URL Patterns with i18n tags
urlpatterns += i18n_patterns(
    path(r'admin/logout/', lambda request: redirect('auth:logout')),
    path(r'admin/', admin.site.urls),
    path(r'authentication/', include('authentication.urls', namespace='auth')),
    path(r'psufrontend/', include('psufrontend.urls', namespace='psufrontend')),
    path(r'', include('homepage.urls', namespace='homepage'))
)
