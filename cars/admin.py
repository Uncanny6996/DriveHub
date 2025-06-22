from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.conf import settings
import os
import joblib
import numpy as np
import pandas as pd
from .models import Car, Reservation
from cardealer.utils.haar_plate_blur import blur_plate_with_haar

class CarAdminForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = '__all__'
        widgets = {
            'market_categories': forms.TextInput(attrs={
                'placeholder': 'Comma-separated values (e.g., Luxury,Performance)'
            }),
        }

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'booking_method', 'visit_date', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'car__car_title')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    form = CarAdminForm
    
    def thumbnail(self, obj):
        if obj.car_photo:
            return format_html(
                '<img src="{}" width="40" style="border-radius: 50px;" />',
                obj.car_photo.url
            )
        return ""
    thumbnail.short_description = 'Car Image'

    list_display = (
        'id', 'thumbnail', 'car_title', 'make', 'model', 
        'year', 'price', 'msrp', 'is_featured', 'stock'
    )
    list_display_links = ('id', 'thumbnail', 'car_title')
    list_editable = ('is_featured',)
    search_fields = (
        'car_title', 'make', 'model', 'vehicle_style', 
        'engine_fuel_type', 'transmission_type', 'vin_no'
    )
    list_filter = (
        'is_featured', 'make', 'model', 'year', 
        'vehicle_style', 'engine_fuel_type', 'stock'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'car_title', 'place', 'city', 'state',
                'latitude', 'longitude'
            )
        }),
        ('ML Prediction Features', {
            'fields': (
                'make', 'model', 'year', 'engine_fuel_type',
                'engine_hp', 'engine_cylinders', 'transmission_type',
                'driven_wheels', 'number_of_doors', 'market_categories',
                'vehicle_size', 'vehicle_style', 'highway_mpg', 'city_mpg',
                'popularity', 'msrp'
            )
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'is_featured')
        }),
        ('Vehicle Details', {
            'fields': (
                'color', 'condition', 'description', 'features',
                'passengers', 'vin_no', 'no_of_owners'
            )
        }),
        ('Images', {
            'fields': (
                'car_photo', 'car_photo_1', 'car_photo_2',
                'car_photo_3', 'car_photo_4'
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        # Convert market_category string to array if needed
        if hasattr(obj, 'market_category') and isinstance(obj.market_category, str):
            obj.market_categories = [x.strip() for x in obj.market_category.split(',')]
        
        # Price prediction logic
        price_before = obj.price
        if not price_before or price_before in [None, 0, '']:
            try:
                model_path = os.path.join(settings.BASE_DIR, 'ml', 'car_price_model.pkl')
                encoder_path = os.path.join(settings.BASE_DIR, 'ml', 'car_encoder.pkl')

                if os.path.exists(model_path) and os.path.exists(encoder_path):
                    model = joblib.load(model_path)
                    encoder = joblib.load(encoder_path)

                    input_data = {
                        'Engine Fuel Type': obj.engine_fuel_type,
                        'Transmission Type': obj.transmission_type,
                        'Driven_Wheels': obj.driven_wheels or 'front wheel drive',
                        'Vehicle Size': obj.vehicle_size or 'Midsize',
                        'Vehicle Style': obj.vehicle_style,
                        'Year': obj.year,
                        'Engine HP': float(obj.engine_hp) if obj.engine_hp else 0,
                        'Engine Cylinders': float(obj.engine_cylinders) if obj.engine_cylinders else 0,
                        'city mpg': obj.city_mpg or 0,
                        'highway MPG': obj.highway_mpg or 0
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

        # Save the model first
        super().save_model(request, obj, form, change)

        # Blur plates on all image fields
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