from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('inquiry/', views.inquiry, name='inquiry'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inquiry/<int:inquiry_id>/delete/', views.delete_inquiry, name='delete_inquiry'),
    path('inquiry/<int:inquiry_id>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiry/<int:inquiry_id>/reply/', views.admin_reply, name='admin_reply'),
]