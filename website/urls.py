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
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns

# URL Patterns without i18n tags
urlpatterns = [
    path(r'psucontrol/', include('psucontrol.urls', namespace='psucontrol')),
]

# URL Patterns with i18n tags
urlpatterns += i18n_patterns(
    path(r'admin/logout/', lambda request: redirect('auth:logout')),
    path(r'admin/', admin.site.urls),
    path(r'authentification/', include('authentification.urls', namespace='auth')),
    path(r'', include('homepage.urls', namespace='homepage'))
)
