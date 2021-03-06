from django.urls import path

import authentification.views as v

app_name = 'authentification'

urlpatterns = [
    path(r'login', v.login_view, name="login"),
    path(r'logout', v.logout_view, name="logout"),
    path(r'edit_user', v.edit_user_view, name="edit_user")
]
