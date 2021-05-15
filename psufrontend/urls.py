from django.urls import path

import psufrontend.views as v

app_name = 'psufrontend'

urlpatterns = [
    path(r'register_psu', v.register_psu_view, name='register_psu'),
    path(r'change_user_permissions', v.change_user_permissions_view, name='change_user_permissions'),
    path(r'change_user_permissions/psu/<int:psu>', v.change_user_permissions_view, name='change_user_permissions'),
    path(r'table/psu/<int:psu>/page/<int:page>', v.table_view, name='table_page_view'),
    path(r'table/', v.table_view, name ='table_view'),
]

