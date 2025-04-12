from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('site', views.check_sites()),

]