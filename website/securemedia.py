from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import path

from psucontrol.models import PSUImage


app_name = 'securemedia'

def psufeed_handler(request, path):
    """
    view to handle the request of a psufeed image
    """
    
    access_granted = False

    user = request.user
    if user.is_authenticated:
        
        # superusers always have access
        if user.is_superuser:
            access_granted = True

    if access_granted:
        if settings.DEBUG:
            # redirect when DEBUG = True (no X-Accel-Redirect support)
            return redirect('/protectedmedia/psufeed/' + path)
        else:
            # create response with X-Accel-Redirect
            res = HttpResponse()
            del res['Content-Type']
            res['X-Accel-Redirect'] = 'protectedmedia/psufeed/' + path
            return res
    else:
        return HttpResponseForbidden()


# urls for securemedia
urlpatterns = [
    path(r'psufeed/<path:path>', psufeed_handler, name='psufeed'),
]