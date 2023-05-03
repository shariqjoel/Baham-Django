from django.urls import path
from . import views

urlpatterns = [
     path('',views.home,name='home'),
     path('baham/about-us',views.about,name='aboutus'),
     path('baham/vehicles',views.view_vehicles,name='vehicles'),
     path('baham/vehicles/create',views.create_vehicle,name='create_vehicle'),
]