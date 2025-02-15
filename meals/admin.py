from django.contrib import admin
from .models import Meal, BazarSchedule

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_choice', 'is_active', 'amount', 'created_at', 'updated_at')
    list_filter = ('meal_choice', 'is_active', 'date')
    search_fields = ('user__username', 'user__email')
    ordering = ('-date',)
    # list_editable = ('is_active')


@admin.register(BazarSchedule)
class BazarScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile_number', 'schedule_date')
    list_filter = ('schedule_date',)
    search_fields = ('name', 'mobile_number', 'user__username')
    ordering = ('-schedule_date',)
