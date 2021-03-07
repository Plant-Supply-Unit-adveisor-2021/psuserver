from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from django.contrib.auth import login, logout, update_session_auth_hash
from django.db import IntegrityError

from authentification.forms import LoginForm, EditProfileForm

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
@csrf_exempt
def edit_profile_view(request):
    """
    view for editing all profile fields without password
    """

    @csrf_protect
    def save_user(request, form):
        try:
            request.user.email = form.cleaned_data['email']
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.darkmode = form.cleaned_data['darkmode']
            request.user.save()
            messages.success(request, _("Successfully updated your profile."))
        except IntegrityError:
            messages.error(request, _("The given e-mail address is already used by another user."))

    user = request.user
    editProfileForm = EditProfileForm(user, request.POST or None)

    # save data if form is submitted
    if request.method == 'POST' and editProfileForm.is_valid():
        save_user(request, editProfileForm)

    return render(request, "authentification/edit_profile.html", context={ 'edit_profile_form': editProfileForm })
