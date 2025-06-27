from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'short_name', 
        'email', 
        'car_title', 
        'status',
        'is_resolved',
        'create_date'
    )
    
    list_display_links = ('id', 'short_name')
    search_fields = ('first_name', 'last_name', 'email', 'car_title')
    list_filter = ('is_resolved', 'create_date')
    list_per_page = 25
    list_editable = ('is_resolved',)
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('car_id', 'car_title', 'message', 'admin_reply', 'is_resolved')
        }),
    )
    
    def short_name(self, obj):
        return f"{obj.first_name} {obj.last_name[0]}."
    short_name.short_description = 'Name'
    
    def status(self, obj):
        return "✔ Resolved" if obj.is_resolved else "⚠ Pending"
    status.short_description = 'Status'