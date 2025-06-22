from django.db import models
from datetime import datetime
from ckeditor.fields import RichTextField
from multiselectfield import MultiSelectField
from django.contrib.postgres.fields import ArrayField
from geopy.geocoders import Nominatim
from django.contrib.auth.models import User

class Car(models.Model):
    # Choices for various options
    province_choice = (
        ('KO', 'Koshi'),
        ('MA', 'Madhesh'),
        ('BA', 'Bagmati'),
        ('GA', 'Gandaki'),
        ('LI', 'Lumbini'),
        ('KA', 'Karnali'),
        ('SU', 'Sudurpaschim'),
    )
    year_choice = [(r, r) for r in range(2000, datetime.now().year + 1)]

    features_choices = (
        ('Cruise Control', 'Cruise Control'),
        ('Audio Interface', 'Audio Interface'),
        ('Airbags', 'Airbags'),
        ('Air Conditioning', 'Air Conditioning'),
        ('Seat Heating', 'Seat Heating'),
        ('Alarm System', 'Alarm System'),
        ('ParkAssist', 'ParkAssist'),
        ('Power Steering', 'Power Steering'),
        ('Reversing Camera', 'Reversing Camera'),
        ('Direct Fuel Injection', 'Direct Fuel Injection'),
        ('Auto Start/Stop', 'Auto Start/Stop'),
        ('Wind Deflector', 'Wind Deflector'),
        ('Bluetooth Handset', 'Bluetooth Handset'),
    )

    door_choices = (
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    )

    # Core Fields
    car_title = models.CharField(max_length=255)
    place = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(choices=province_choice, max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # ML Prediction Features
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100)
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    engine_fuel_type = models.CharField(max_length=50)
    engine_hp = models.IntegerField(null=True, blank=True)
    engine_cylinders = models.IntegerField(null=True, blank=True)
    transmission_type = models.CharField(max_length=100)
    driven_wheels = models.CharField(max_length=100, blank=True)
    number_of_doors = models.CharField(max_length=10, choices=door_choices)
    market_categories = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    vehicle_size = models.CharField(max_length=100, blank=True)
    vehicle_style = models.CharField(max_length=100)
    highway_mpg = models.IntegerField(null=True, blank=True)
    city_mpg = models.IntegerField(null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    msrp = models.IntegerField(null=True, blank=True)

    # Display Fields
    color = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    price = models.IntegerField(null=True, blank=True)
    description = RichTextField()
    car_photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    car_photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    car_photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    car_photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    car_photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    features = MultiSelectField(choices=features_choices)
    passengers = models.IntegerField()
    vin_no = models.CharField(max_length=100)
    no_of_owners = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=1)
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.car_title

    def save(self, *args, **kwargs):
        # Geocoding logic remains the same
        super().save(*args, **kwargs)

    def geocode_location(self, place, city, state):
        geolocator = Nominatim(user_agent="car_location_app")
        location = geolocator.geocode(f"{place}, {city}, {state}, Nepal")
        if location:
            return {'lat': location.latitude, 'lon': location.longitude}
        return {'lat': None, 'lon': None}

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    booking_method = models.CharField(max_length=100, default='Online')
    visit_date = models.DateTimeField(default=datetime.now)
    delivery_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for {self.car.car_title} by {self.user.username}"