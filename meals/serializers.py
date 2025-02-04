from .models import Meal
from rest_framework import serializers
class AdminMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = [
            'id', 'user', 'date', 'meal_choice', 'is_active', 'amount', 'is_paid', 'created_at', 'updated_at'
        ]

class UserMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = [
            'id', 'user', 'date', 'meal_choice', 'is_active', 'amount', 'is_paid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['is_active', 'is_paid', 'amount', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        meal_choice = validated_data.get('meal_choice')
        amount = Meal.MEAL_PRICES.get(meal_choice, 0)
        validated_data['amount'] = amount
        
        return super().create(validated_data)

