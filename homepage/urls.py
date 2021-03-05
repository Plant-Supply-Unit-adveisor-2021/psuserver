from django.urls import path

import homepage.views as v

app_name = 'homepage'

urlpatterns = [
    path('', v.startpage, name='index'),
]
