from django.urls import path

import psufrontend.views as v

app_name = 'psufrontend'

urlpatterns = [
    path(r'register_psu', v.register_psu_view, name='register_psu'),
    path(r'table/psu/<int:psu>', v.table_view, name='table'),
    path(r'table', v.table_view, name='table'),
    path(r'no_psu', v.no_psu_view, name='no_psu'),
    path(r'add_watering_task', v.add_watering_task_view, name='add_watering_task'),
    path(r'watering_control', v.watering_control_view, name='watering_control'),
    path(r'dashboard', v.dashboard_view, name='dashboard'),
]
