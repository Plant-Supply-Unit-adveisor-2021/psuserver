from django.urls import path

import authentification.views as v

app_name = 'authentification'

urlpatterns = [
    path(r'login', v.login_view, name="login"),
    path(r'logout', v.logout_view, name="logout"),
    path(r'edit_profile', v.edit_profile_view, name="edit_profile"),
    path(r'register', v.register_view, name="register"),
    path(r'welcome', v.register_after_view, name="register_after"),
]
