from django.urls import path

import authentification.views as v

app_name = 'authentification'

urlpatterns = [
    path('login', v.login_view, name="login"),
]
