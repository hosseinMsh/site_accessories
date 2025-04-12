from django.urls import path

from core.views import check_sites

app_name = 'core'

urlpatterns = [
    path('site/', check_sites,name='check_sites'),

]