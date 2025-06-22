from django.urls import path
from . import views

urlpatterns = [
    path('', views.cars, name='cars'),
    path('<int:id>/buy/', views.buy_car, name='buy_car'),
    path('reservation/<int:id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('<int:id>/', views.car_detail, name='car_detail'),
    path('search/', views.search, name='search'),
    path('image-search/', views.image_search, name='image_search'),
]
