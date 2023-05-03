from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Vehicle(models.Model):
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    VEHICLE_TYPE_CHOICES = [
        ('MC', 'Motorcycle'),
        ('SD', 'Sedan'),
        ('HB', 'Hatchback'),
        ('SUV', 'SUV'),
        ('VN', 'Van'),
    ]
    type = models.CharField(max_length=3, choices=VEHICLE_TYPE_CHOICES)
    sitting_capacity = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=20, unique=True)
    status_choices = [
        ('EM', 'Empty'),
        ('FL', 'Full'),
        ('IA', 'Inactive'),
    ]
    status = models.CharField(max_length=2, choices=status_choices)
    front_picture = models.ImageField(upload_to='vehicle_images')
    side_picture = models.ImageField(upload_to='vehicle_images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_vehicles')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_vehicles')

    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.registration_number})"

    def delete(self, *args, **kwargs):
        if not self.updated_by.is_staff:
            raise ValueError("Only staff members can delete vehicles.")
        super().delete(*args, **kwargs)

class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    contact_numbers = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    landmark = models.CharField(max_length=100)
    town = models.CharField(max_length=50)
    gps_coordinates = models.CharField(max_length=50)
    bio = models.TextField(blank=True)
    affiliated_as_choices = [
        ('ST', 'Student'),
        ('FC', 'Faculty'),
        ('SF', 'Staff'),
    ]
    affiliated_as = models.CharField(max_length=2, choices=affiliated_as_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_profiles')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_profiles')
    is_active = models.BooleanField(default =True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"

    def delete(self, *args, **kwargs):
        if not self.updated_by.is_staff:
            raise ValueError("Delete Permission Denied! Only Staff Members are allowed to delete")
        super().delete(*args, **kwargs)


class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    date_joined = models.DateTimeField(auto_now_add=True)
    num_contracts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"


class Companion(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='companion_profile')
    currently_in_contract = models.BooleanField(default=False)

    #audit fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companions_created')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companions_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"

    def delete(self, *args, **kwargs):
        if not self.user.is_staff:
            raise ValueError("Delete Permission Denied! Only Staff Members are allowed to delete")
        super().delete(*args, **kwargs)

class Contract(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    companion = models.ForeignKey(Companion, on_delete=models.CASCADE)
    effective_start_date = models.DateField()
    expiry_date = models.DateField()
    fuel_share = models.DecimalField(max_digits=3, decimal_places=2)
    maintenance_share = models.DecimalField(max_digits=3, decimal_places=2)
    schedule = models.DateTimeField()

    # audit fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts_created')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts_updated')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # validations
    def clean(self):
        if self.vehicle.owner.user.affiliation not in ['student', 'faculty', 'staff']:
            raise ValidationError("Only students, faculty members, and staff members are allowed to use the service.")
        if Contract.objects.filter(vehicle=self.vehicle).count() > 0:
            raise ValidationError("Only one contract per vehicle owner is allowed.")
        if self.vehicle.sitting_capacity < len(self.schedule):
            raise ValidationError("The number of passengers must not exceed the vehicle's seating capacity.")
        if Vehicle.objects.filter(registration_number=self.vehicle.registration_number).exclude(pk=self.vehicle.pk).exists():
            raise ValidationError("The registration number must be unique.")
        if self.fuel_share + self.maintenance_share > 1:
            raise ValidationError("The total share cannot exceed 100%.")
        if (self.expiry_date - self.effective_start_date).days > 180:
            raise ValidationError("The contract must not last longer than 6 months and should terminate automatically.")
        if self.companion.currently_in_contract:
            raise ValidationError("A companion cannot have multiple active contracts simultaneously.")

    def __str__(self):
        return self.vehicle.manufacturer + ' ' + self.vehicle.model + ' - ' + self.companion.user.first_name + ' ' + self.companion.user.last_name
    
    def delete(self, *args, **kwargs):
        if not self.user.is_staff:
            raise ValueError("Delete Permission Denied! Only Staff Members are allowed to delete")
        super().delete(*args, **kwargs)

