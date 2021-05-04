from django.core.exceptions import PermissionDenied, ViewDoesNotExist
from django.http import Http404
from django.urls import path

app_name = 'errorviews'


def view_404(request):
    """
    view to show the 404 page with Webserver 404 error
    """
    raise Http404('Webserver404')


def view_403(request):
    """
    view to show the 404 page with Webserver 404 error
    """
    raise PermissionDenied('Webserver403')


def view_500(request):
    """
    view to show the 404 page with Webserver 404 error
    """
    raise ViewDoesNotExist('NONE')


# error urls
urlpatterns = [
    path(r'404', view_404, name='404'),
    path(r'403', view_403, name='403'),
    path(r'500', view_500, name='500')
]