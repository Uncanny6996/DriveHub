from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    car_id = models.IntegerField()
    customer_need = models.CharField(max_length=100)
    car_title = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    user_id = models.IntegerField(blank=True)
    create_date = models.DateTimeField(blank=True, default=datetime.now)
    
    # New fields for inquiry system
    admin_reply = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Admin Reply",
        help_text="Enter your reply to the customer here"
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name="Mark as Resolved",
        help_text="Check this box when the inquiry is handled"
    )
    reply_date = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Reply Date"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    def __str__(self):
        return f"Inquiry #{self.id} - {self.email}"

    def save(self, *args, **kwargs):
        # Update reply_date when admin_reply is set
        if self.admin_reply and not self.reply_date:
            self.reply_date = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-create_date']
        verbose_name = "Customer Inquiry"
        verbose_name_plural = "Customer Inquiries"