from django.urls import path

import psufrontend.views as v

app_name = 'psufrontend'

urlpatterns = [
    path(r'register_psu', v.register_psu_view, name='register_psu'),
    path(r'table/psu/<int:psu>', v.table_view, name='table'),
    path(r'table', v.table_view, name='table'),
    path(r'no_psu', v.no_psu_view, name='no_psu'),
    path(r'add_watering_task', v.add_watering_task_view, name='add_watering_task'),
    path(r'chart/psu/<int:psu>/<int:day>', v.chart_view, name='chart'),
    path(r'chart/psu/<int:psu>', v.chart_view, name='chart'),
    path(r'chart', v.chart_view, name='chart'),
]
