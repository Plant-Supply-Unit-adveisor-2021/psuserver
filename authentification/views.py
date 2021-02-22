from django.shortcuts import render

from django.contrib.auth import login, logout

from authentification.forms import LoginForm

# Create your views here.

def login_view(request):
    """
    View for Login
    """

    """
    ToDo after @login_required becomes a topic

    if 'next' in request.GET:
        next_page = request.GET['next']
    else:
        next_page = "/"
    """


    login_form = LoginForm(request.POST or None)
    if request.POST and login_form.is_valid():
        user = login_form.login(request)
        if user:
            login(request, user)
    return render(request, 'authentification/login.html', {'login_form': login_form})