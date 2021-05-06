from django.urls import path

import psucontrol.views as v

app_name = 'psucontrol'

urlpatterns = [
    path(r'register_new_psu', v.register_new_psu, name="register_new_psu"),
    path(r'get_challenge', v.get_challenge, name="get_challenge"),
    path(r'add_data_measurement', v.add_data_measurement, name="add_data_measurement"),
    path(r'add_image', v.add_image, name="add_image"),
    path(r'get_watering_task', v.get_watering_task, name="get_watering_task"),
    path(r'mark_watering_task_executed', v.mark_watering_task_executed, name="mark_watering_task_executed"),
]
