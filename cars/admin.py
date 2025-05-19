from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
import os

from .models import Car, Reservation
from cardealer.utils.haar_plate_blur import blur_plate_with_haar
  # ✅ Updated import

# Reservation Admin
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'booking_method', 'visit_date', 'created_at', 'status')

# Car Admin
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        return format_html(
            '<img src="{}" width="40" style="border-radius: 50px;" />',
            obj.car_photo.url
        )
    thumbnail.short_description = 'Car Image'

    list_display = ('id', 'thumbnail', 'car_title', 'city', 'price', 'condition', 'body_style', 'fuel_type', 'is_featured', 'year')
    list_display_links = ('id', 'thumbnail', 'car_title')
    list_editable = ('is_featured',)
    search_fields = ('id', 'car_title', 'city', 'condition', 'body_style', 'fuel_type')
    list_filter = ('city', 'model', 'body_style', 'fuel_type')

    fieldsets = (
        (None, {
            'fields': (
                'car_title', 'place', 'city', 'state', 'latitude', 'longitude',
                'price', 'color', 'model', 'year', 'condition', 'body_style'
            )
        }),
        ('Description', {
            'fields': (
                'description', 'car_photo', 'car_photo_1', 'car_photo_2',
                'car_photo_3', 'car_photo_4'
            )
        }),
        ('Other Info', {
            'fields': (
                'features', 'engine', 'transmission', 'interior', 'miles',
                'doors', 'passengers', 'vin_no', 'milage', 'fuel_type',
                'no_of_owners', 'stock', 'is_featured'
            )
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[0][1]['fields'] = (
            'car_title', 'place', 'city', 'state', 'latitude', 'longitude',
            'price', 'color', 'model', 'year', 'condition', 'body_style'
        )
        return fieldsets

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        image_fields = ['car_photo', 'car_photo_1', 'car_photo_2', 'car_photo_3', 'car_photo_4']
        for field in image_fields:
            image = getattr(obj, field)
            if image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(image))
                try:
                    print(f"[BLUR START] Trying to blur: {image_path}")
                    blur_plate_with_haar(image_path)  # ✅ Haar Cascade blur
                    print(f"[BLUR DONE] Finished blurring: {image_path}")
                except Exception as e:
                    print(f"[BLUR ERROR] {field}: {e}")

                    

