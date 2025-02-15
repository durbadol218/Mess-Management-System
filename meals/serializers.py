from .models import Meal
from .models import BazarSchedule
from rest_framework import serializers
from user.models import User_Model
class AdminMealSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Meal
        fields = ['id', 'user', 'username', 'date', 'meal_choice', 'is_active', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['amount', 'created_at', 'updated_at']

class UserMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'user', 'date', 'meal_choice', 'is_active', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['amount', 'created_at', 'updated_at']

    def perform_create(self, serializer):
        meal_choice = serializer.validated_data.get('meal_choice')
        amount = Meal.MEAL_PRICES.get(meal_choice, 0)
        serializer.save(user=self.request.user, amount=amount)


class BazarScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BazarSchedule
        fields = ['id','name', 'mobile_number', 'schedule_date']
