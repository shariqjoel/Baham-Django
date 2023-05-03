from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Vehicle
from .enum_types import VehicleTypes

# Create your views here.


def home(request):
    template = loader.get_template(template_name='home.html')
    context = {
        'title': 'Home',
        'heading': 'Welcome to Baham',
    }
    return HttpResponse (template.render(context,request=request))

def about(request):
    context = {
        'title': 'About Us',
        'heading': 'Welcome to Baham',
    }
    template = loader.get_template(template_name='about.html')
    return HttpResponse (template.render(context,request=request))



def create_vehicle(request):
    template = loader.get_template(template_name='createVehicle.html')
    context = {
    'title': 'Vehicles',
    'heading': 'Welcome to Baham',
    'vehicle_types': [t for t in VehicleTypes]
    }

    return HttpResponse (template.render(context,request=request))
    


def save_vehicle(request):
    vendor = request.POST.get('vendor')
    model = request.POST.get('model')
    # vehicle_type = request.POST.get('vehicle_type')
    vehicle = Vehicle(vendor=vendor, model=model)
    vehicle.save()
    return view_vehicles(request)


def view_vehicles(request):
    template = loader.get_template(template_name='Vehicle.html')
    vehicles = Vehicle.objects.all().order_by('vendor')
    context = {
        'title': 'Vehicles',
        'heading': 'Welcome to Baham',
        'vehicles':  vehicles,
    }
    return HttpResponse (template.render(context,request=request))

