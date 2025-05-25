from django.db import models
from datetime import datetime
from ckeditor.fields import RichTextField
from multiselectfield import MultiSelectField
from geopy.geocoders import Nominatim  # Import geocoder
from django.contrib.auth.models import User

# ------------------------
# Car Model
# ------------------------

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
    year_choice = [(r, r) for r in range(2000, datetime.now().year + 1)]  # Ensuring valid years

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

    # Fields
    car_title = models.CharField(max_length=255)
    place = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(choices=province_choice, max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Other fields
    color = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(('year'), choices=year_choice, default=datetime.now().year)  # Default year is set
    condition = models.CharField(max_length=100)
    price = models.IntegerField(null=True, blank=True)
    description = RichTextField()
    car_photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    car_photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    car_photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    car_photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    car_photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    features = MultiSelectField(choices=features_choices)
    body_style = models.CharField(max_length=100)
    engine = models.CharField(max_length=100)
    transmission = models.CharField(max_length=100)
    interior = models.CharField(max_length=100)
    miles = models.IntegerField()
    doors = models.CharField(choices=door_choices, max_length=10)
    passengers = models.IntegerField()
    vin_no = models.CharField(max_length=100)
    milage = models.IntegerField()
    fuel_type = models.CharField(max_length=50)
    no_of_owners = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=1)
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.car_title

    def save(self, *args, **kwargs):
        # Automatically update the latitude and longitude based on place, city, and state
        #if self.place and self.city and self.state:
         ###     self.latitude = location['lat']
            #    self.longitude = location['lon']
        super().save(*args, **kwargs)

    def geocode_location(self, place, city, state):
        # Using Geopy's Nominatim geocoder to get latitude and longitude
        geolocator = Nominatim(user_agent="car_location_app")
        location = geolocator.geocode(f"{place}, {city}, {state}, Nepal")
        if location:
            return {'lat': location.latitude, 'lon': location.longitude}
        return {'lat': None, 'lon': None}



# ------------------------
# Reservation Model
# ------------------------
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

