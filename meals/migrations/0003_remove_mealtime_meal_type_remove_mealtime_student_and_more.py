# Generated by Django 5.1.5 on 2025-01-26 15:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_alter_mealtype_description'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mealtime',
            name='meal_type',
        ),
        migrations.RemoveField(
            model_name='mealtime',
            name='student',
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('meal_choice', models.CharField(choices=[('full', 'Full Meal'), ('guest', 'Guest Meal'), ('half_day', 'Lunch & Breakfast'), ('half_night', 'Dinner & Breakfast')], default='full', max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('amount', models.FloatField()),
                ('is_paid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='user.user_model')),
            ],
        ),
        migrations.DeleteModel(
            name='MealBill',
        ),
        migrations.DeleteModel(
            name='MealType',
        ),
        migrations.DeleteModel(
            name='MealTime',
        ),
    ]
