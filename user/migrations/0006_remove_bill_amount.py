# Generated by Django 5.1.5 on 2025-02-15 03:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_remove_bill_name_bill_total_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='amount',
        ),
    ]
