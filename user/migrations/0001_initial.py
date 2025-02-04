# Generated by Django 5.1.5 on 2025-01-19 04:32

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.utils.timezone
import user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('reg_no', models.CharField(blank=True, default=user.models.generate_registration_number, max_length=100, null=True, unique=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$', 'Invalid registration number')])),
                ('full_name', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('education_details', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15, unique=True, validators=[django.core.validators.RegexValidator('^\\+?\\d{10,15}$', 'Invalid contact number')])),
                ('user_type', models.CharField(choices=[('Admin', 'Admin'), ('User', 'User')], max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='student_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='student_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
