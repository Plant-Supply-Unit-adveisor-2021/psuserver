from django.shortcuts import render

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from authentification.forms import LoginForm
from django.http import HttpResponseRedirect

# Create your views here.

def login_view(request):
    """
    View for Login
    """

    # redirect to requested page which needs an authentification
    # otherwise redirect to startpage
    if 'next' in request.GET:
        next_page = request.GET['next']
    else:
        next_page = "/" 
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(next_page)


    login_form = LoginForm(request.POST or None)
    if request.POST and login_form.is_valid():
        user = login_form.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect(next_page)
    return render(request, 'authentification/login.html', {'login_form': login_form})

def logout_view(request):
    """
    view for logging out
    """
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect("/")

@login_required
def edit_profile_view(request):
    """
    view for editing all profile fields without password
    """
    
    return render(request, "authentification/edit_profile.html")
