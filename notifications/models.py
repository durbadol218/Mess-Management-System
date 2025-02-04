# from django.db import models
# from user.models import User_Model
# # Create your models here.
# class Notification(models.Model):
#     user = models.ForeignKey(User_Model, on_delete=models.CASCADE)
#     message = models.TextField()
#     notification_type = models.CharField(max_length=100)
#     date_sent = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Notification for {self.user.username}: {self.message[:50]}"

from django.db import models
from user.models import User_Model
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('MEAL_BOOK', 'Meal Book'),
        ('MEAL_BOOK_CANCEL', 'Meal Book Cancel'),
        ('MEAL_BOOK_UPDATE', 'Meal Book Update'),
        ('MEAL_BOOK_REMINDER', 'Meal Book Reminder'),
        ('MESS_RENT', 'Mess Rent'),
        ('BILL', 'Bill'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User_Model, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.notification_type}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
        
    class Meta:
        ordering = ['-created_at']
