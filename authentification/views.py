from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages

from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.db import IntegrityError

from authentification.forms import LoginForm, EditProfileForm, ChangePasswordForm, RegisterForm
from authentification.models import User

# Create your views here.

def login_view(request):
    """
    View for Login
    """

    # redirect to requested page which needs an authentification
    # otherwise redirect to startpage
    next_page = "/" 
    if 'next' in request.GET:
        next_page = request.GET['next']
    
    if request.user.is_authenticated:
        return redirect(next_page)


    login_form = LoginForm(request.POST or None)
    if request.POST and login_form.is_valid():
        login(request, login_form.cleaned_data['user'])
        return redirect(next_page)
    return render(request, 'authentification/login.html', {'login_form': login_form})

def logout_view(request):
    """
    view for logging out
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect("/")

@login_required
@csrf_exempt
def edit_profile_view(request):
    """
    view for editing all profile fields and the password
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

    @csrf_protect
    def change_passwd(request, form):
        print("SET PASSWD TO: "+form.cleaned_data['new_passwd_1'])
        request.user.set_password(form.cleaned_data['new_passwd_1'])
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, _("Successfully updated your password."))


    user = request.user
    editProfileForm = EditProfileForm(user, request.POST or None)
    changePasswdForm = ChangePasswordForm(user, request.POST or None)

    # save data if form is submitted
    if request.method == 'POST':
        if editProfileForm.is_valid():
            save_user(request, editProfileForm)
        if changePasswdForm.is_valid():
            if changePasswdForm.cleaned_data['old_passwd'] != '':
                change_passwd(request, changePasswdForm)

    return render(request, "authentification/edit_profile.html", context={ 'edit_profile_form': editProfileForm, 'change_passwd_form': changePasswdForm})

def register_view(request):
    """
    view for creating a new user
    ALL new users are not activated and the only way to do so is via the admin panel
    """
    if request.user.is_authenticated:
        return redirect("/")

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = User(email=form.cleaned_data['email'], first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'], is_active=False)
        user.set_password(form.cleaned_data['passwd_1'])
        user.save()
        return redirect('auth:register_after')

    return render(request, "authentification/register.html", context={'register_form':form})

def register_after_view(request):
    return render(request, "authentification/after_register.html")
