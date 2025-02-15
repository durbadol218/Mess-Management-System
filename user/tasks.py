# bills/tasks.py

from celery import shared_task
from .models import Bill, User_Model
from datetime import timedelta
from django.utils import timezone

@shared_task
def generate_bills_task():
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month.replace(month=today.month + 1) - timedelta(days=1)).date()

    recurring_bills = [
        ('mess_rent', 950.00),
        ('water', 100.00),
        ('khala', 50.00),
        ('net', 75.00),
        ('current', 150.00),
    ]

    for user in User_Model.objects.all():
        for bill_type, amount in recurring_bills:
            Bill.objects.create(
                user=user,
                name=f'{bill_type.capitalize()} Bill',
                bill_type=bill_type,
                amount=amount,
                due_date=end_of_month,
            )

