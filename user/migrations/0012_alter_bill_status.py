# Generated by Django 5.1.5 on 2025-06-18 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_bill_payment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')], default='Pending', max_length=20),
        ),
    ]
