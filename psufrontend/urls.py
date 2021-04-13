from django.urls import path

import psufrontend.views as v

app_name = 'psufrontend'

urlpatterns = [
    path(r'register_psu', v.register_psu_view, name='register_psu'),
    path(r'table/', v.table_view, name ='table_view'),
    path(r'table/table_id<int:num>/', v.table_id),
]

