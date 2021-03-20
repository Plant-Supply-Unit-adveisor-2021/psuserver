from django.urls import path

import psucontrol.views as v

app_name = 'psucontrol'

urlpatterns = [
    path(r'register_new_psu', v.register_new_psu, name="register_new_psu"),
    path(r'get_challenge', v.get_challenge, name="get_challenge"),
    path(r'add_data_measurement', v.add_data_measurement, name="add_data_measurement")
]
