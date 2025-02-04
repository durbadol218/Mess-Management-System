from django.contrib import admin
from .models import Meal

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_choice', 'is_active', 'amount', 'is_paid', 'created_at', 'updated_at')  # Columns in admin list view
    list_filter = ('meal_choice', 'is_active', 'is_paid', 'date')  # Filters in the sidebar
    search_fields = ('user__username', 'user__email')  # Search by username or email
    ordering = ('-date',)  # Order by most recent date
    list_editable = ('is_active', 'is_paid')  # Allow inline editing of these fields

