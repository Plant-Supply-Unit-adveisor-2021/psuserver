from django.urls import path

import psufrontend.views as v

app_name = 'psufrontend'

urlpatterns = [
    path(r'register_psu', v.register_psu_view, name='register_psu'),
]
