from django.urls import path

import psufrontend.views as v

app_name = 'psufrontend'

urlpatterns = [
    path(r'register_psu', v.register_psu_view, name='register_psu'),
    path(r'change_user_permissions/psu/<int:psu>', v.change_user_permissions_view, name='change_user_permissions'),
    path(r'change_user_permissions/', v.change_user_permissions_view, name='change_user_permissions'),
    path(r'table/psu/<int:psu>', v.table_view, name='table'),
    path(r'table', v.table_view, name='table'),
    path(r'no_psu', v.no_psu_view, name='no_psu'),
    path(r'add_watering_task/psu/<int:psu>', v.add_watering_task_view, name='add_watering_task'),
    path(r'add_watering_task', v.add_watering_task_view, name='add_watering_task'),
    path(r'watering_control/psu/<int:psu>', v.watering_control_view, name='watering_control'),
    path(r'watering_control', v.watering_control_view, name='watering_control'),
    path(r'dashboard/psu/<int:psu>', v.dashboard_view, name='dashboard'),
    path(r'dashboard', v.dashboard_view, name='dashboard'),
    path(r'chart/psu/<int:psu>/<str:time_range>', v.chart_view, name='chart'),
    path(r'chart/psu/<int:psu>', v.chart_view, name='chart'),
    path(r'chart', v.chart_view, name='chart'),
]
