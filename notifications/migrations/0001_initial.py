# Generated by Django 5.1.5 on 2025-02-05 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('MEAL_BOOK', 'Meal Book'), ('MEAL_BOOK_CANCEL', 'Meal Book Cancel'), ('MEAL_BOOK_UPDATE', 'Meal Book Update'), ('MEAL_BOOK_REMINDER', 'Meal Book Reminder'), ('MESS_RENT', 'Mess Rent'), ('BILL', 'Bill'), ('OTHER', 'Other')], max_length=20)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
