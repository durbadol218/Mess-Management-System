# Generated by Django 5.1.5 on 2025-02-14 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_bill'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='admin_reply',
            field=models.TextField(blank=True, null=True),
        ),
    ]
