from django.db import models
# from user.models import User_Model
from django.db.models import Sum
from django.conf import settings
from django.db import models
from django.db.models import Count


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

    user = models.ForeignKey('user.User_Model', on_delete=models.CASCADE, related_name="meals")
    date = models.DateField()
    meal_choice = models.CharField(max_length=15, choices=MEAL_CHOICES, default="full")
    is_active = models.BooleanField(default=True)
    amount = models.FloatField()
    # is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.amount = self.MEAL_PRICES.get(self.meal_choice, 0)
        super().save(*args, **kwargs)
        
    def get_total_meal_amount(user_id):
        total_amount = Meal.objects.filter(user_id=user_id).aggregate(Sum('amount'))
        return total_amount['amount__sum'] or 0
        
    def __str__(self):
        user_name = self.user.username if self.user else "No User"
        return f"{user_name} - {self.meal_choice} on {self.date}"
    
    @classmethod
    def count_meals_for_user(cls, user_id, year, month):
        meals = (
            cls.objects.filter(user_id=user_id, date__year=year, date__month=month)
            .values("meal_choice")
            .annotate(count=Count("meal_choice"))
        )
        meal_counts = {meal["meal_choice"]: meal["count"] for meal in meals}
        return {
            "full_meal": meal_counts.get("full", 0),
            "guest_meal": meal_counts.get("guest", 0),
            "half_day_meal": meal_counts.get("half_day", 0),
            "half_night_meal": meal_counts.get("half_night", 0),
        }

class BazarSchedule(models.Model):
    user = models.ForeignKey('user.User_Model', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    schedule_date = models.DateField()
    # is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.schedule_date}"

