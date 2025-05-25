from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
import os
import joblib
import numpy as np
import pandas as pd

from .models import Car, Reservation
from cardealer.utils.haar_plate_blur import blur_plate_with_haar


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'booking_method', 'visit_date', 'created_at', 'status')


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

    def save_model(self, request, obj, form, change):
        # Predict price only if not set
        price_before = obj.price

        if not price_before or price_before in [None, 0, '']:
            try:
                model_path = os.path.join(settings.BASE_DIR, 'ml', 'car_price_model.pkl')
                encoder_path = os.path.join(settings.BASE_DIR, 'ml', 'car_encoder.pkl')

                model = joblib.load(model_path)
                encoder = joblib.load(encoder_path)

                input_data = {
                    'Engine Fuel Type': obj.fuel_type,
                    'Transmission Type': obj.transmission,
                    'Driven_Wheels': 'front wheel drive',
                    'Vehicle Size': 'Midsize',
                    'Vehicle Style': obj.body_style,
                    'Year': obj.year,
                    'Engine HP': float(obj.engine) if obj.engine else 0,
                    'Engine Cylinders': float(obj.no_of_owners) if obj.no_of_owners else 0,
                    'city mpg': obj.milage,
                    'highway MPG': obj.milage
                }

                df = pd.DataFrame([input_data])
                df_encoded = encoder.transform(df)
                log_price = model.predict(df_encoded)
                predicted_price = int(np.expm1(log_price)[0])
                obj.price = predicted_price

                print(f"[✅ ML] Predicted price set to: {predicted_price}")
            except Exception as e:
                print(f"[❌ ML ERROR] Could not predict price: {e}")
        else:
            print(f"[ℹ️ SKIPPED ML] Price manually set: {price_before}")

        # Save model
        super().save_model(request, obj, form, change)

        # Blur plates
        image_fields = ['car_photo', 'car_photo_1', 'car_photo_2', 'car_photo_3', 'car_photo_4']
        for field in image_fields:
            image = getattr(obj, field)
            if image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(image))
                try:
                    blur_plate_with_haar(image_path)
                    print(f"[✅ BLUR DONE] {field}")
                except Exception as e:
                    print(f"[❌ BLUR ERROR] {field}: {e}")
