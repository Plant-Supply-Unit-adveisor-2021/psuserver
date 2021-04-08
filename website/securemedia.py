from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import path

from psucontrol.models import PSUImage
from psucontrol.utils import check_permissions


app_name = 'securemedia'

@login_required
def psufeed_handler(request, path):
    """
    view to handle the request of a psufeed image
    """

    # try matching path to PSUImage in database and getting the corresponding psu
    try:
        psu = PSUImage.objects.get(image='psufeed/' + path).psu
    except PSUImage.DoesNotExist:
        # no such image found
        return HttpResponseNotFound()
    
    if check_permissions(psu, request.user) > 0:
        # grant access to owner and permitted users
        # staff/superusers treated as owners

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