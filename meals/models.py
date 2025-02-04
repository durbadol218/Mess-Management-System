from django.db import models
from user.models import User_Model
from django.db.models import Sum
from django.conf import settings

class Meal(models.Model):
    MEAL_CHOICES = [
        ("full", "Full Meal"),
        ("guest", "Guest Meal"),
        ("half_day", "Lunch & Breakfast"),
        ("half_night", "Dinner & Breakfast"),
    ]
    MEAL_PRICES = {
        "full": 65,
        "guest": 60,
        "half_day": 40,
        "half_night": 40,
    }

    user = models.ForeignKey(User_Model, on_delete=models.SET_NULL, related_name="meals", null=True, blank=True)
    date = models.DateField()
    meal_choice = models.CharField(max_length=15, choices=MEAL_CHOICES, default="full")
    is_active = models.BooleanField(default=True)
    amount = models.FloatField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.amount = self.MEAL_PRICES.get(self.meal_choice, 0)
        super().save(*args, **kwargs)
        
    def get_total_meal_amount(user_id):
        total_amount = Meal.objects.filter(user_id=user_id).aggregate(Sum('amount'))
        return total_amount['amount__sum'] or 0
        
    def __str__(self):
        return f"{self.user.username} - {self.meal_choice} on {self.date} (Paid: {self.is_paid})"
