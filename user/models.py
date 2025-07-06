from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models
from .constants import USER_TYPE
import random, string
from django.conf import settings
from django.utils.timezone import now
import binascii
import os
import uuid
from meals.models import Meal
from django.db.models import Count
from decimal import Decimal
from django.core.exceptions import ValidationError

# from rest_framework.authtoken.models import Token as DefaultToken

def generate_registration_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class User_Model(AbstractUser):
    reg_no = models.CharField(max_length=100, unique=True, default=generate_registration_number, validators=[RegexValidator(r'^[A-Za-z0-9]+$', 'Invalid registration number')], blank=True, null=True)
    email = models.EmailField(max_length=50,unique=True)
    education_details = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15,unique=True,validators=[RegexValidator(r'^\+?\d{10,15}$', 'Invalid contact number')])
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    is_approved = models.BooleanField(default=False)
    joined_date = models.DateField(auto_now_add=True)
    address = models.CharField(max_length=255,default="Unknown Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(upload_to='student_profiles/', blank=True, null=True)


    groups = models.ManyToManyField(Group, blank=True)
    user_permissions = models.ManyToManyField(Permission, blank=True)
    SEAT_CHOICES = [
    ('double_bed', 'Double Bed Room'),
    ('private', 'Private Room'),]
    seat_type = models.CharField(max_length=20, choices=SEAT_CHOICES, default='double_bed')
    seat_rent = models.DecimalField(max_digits=10, decimal_places=2, default=950.00)
    
    def save(self, *args, **kwargs):
        if self.seat_type == 'private':
            self.seat_rent = 1100.00
        else:
            self.seat_rent = 950.00
        super().save(*args, **kwargs)



class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('water', 'Water'),
        ('electricity', 'Electricity'),
        ('food', 'Food'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    ]
    
    STATUS_PENDING = 'pending'
    STATUS_RESOLVED = 'resolved'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    user = models.ForeignKey(User_Model, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default=STATUS_PENDING, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    active_complaint = models.BooleanField(default=True)
    
    
    
    def save(self, *args, **kwargs):
        if self.status == self.STATUS_RESOLVED and not self.resolved_at:
            from django.utils.timezone import now
            self.resolved_at = now()
            self.active_complaint = False
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Complaint from {self.user.username} - {self.category} - {self.status}"

    class Meta:
        ordering = ['-created_at']

class CustomToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE
    )
    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

class Bill(models.Model):
    BILL_TYPES = [
        ('mess_rent', 'Mess Rent'),
        ('water', 'Water Bill'),
        ('khala', 'Khala Bill'),
        ('net', 'Net Bill'),
        ('current', 'Current Bill'),
        ('other', 'Other'),
    ]

    FIXED_BILL_AMOUNTS = {
    'mess_rent': Decimal('0.00'),
    'water': Decimal('200.00'),
    'khala': Decimal('300.00'),
    'net': Decimal('70.00'),
    'current': Decimal('150.00'),
    'other': Decimal('0.00'),
}


    
    user = models.ForeignKey(User_Model, on_delete=models.CASCADE, related_name='bills')
    # bill_type = models.CharField(max_length=20, choices=BILL_TYPES,default='all')
    bill_type = models.CharField(max_length=20, choices=[
        ('all_fixed', 'All Fixed Bills'),
        ('mess_rent', 'Mess Rent'),
        ('water', 'Water'),
        ('khala', 'Khala'),
        ('net', 'Internet'),
        ('current', 'Electricity'),
        ('other', 'Other'),
    ], default='all_fixed')
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default='Pending', choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')])
    payment_date = models.DateTimeField(null=True, blank=True)
    
    @staticmethod
    def calculate_meal_bill(user, year, month):
        from meals.models import Meal
        meal_counts = Meal.objects.filter(user=user, date__year=year, date__month=month,is_active=True).values('meal_choice').annotate(count=models.Count('meal_choice'))
        meal_dict = {entry['meal_choice']: entry['count'] for entry in meal_counts}
        total_bill = sum(Meal.MEAL_PRICES.get(meal_choice, 0) * count for meal_choice, count in meal_dict.items())
        return {
            "meals": meal_dict,
            "total": total_bill
        }

    # def calculate_total_bill(self):
    #     year = self.due_date.year
    #     month = self.due_date.month
    #     meal_bill = Bill.calculate_meal_bill(self.user, year, month)['total']
    #     if self.bill_type == 'all_fixed':
    #         fixed_bill_total = (
    #         self.user.seat_rent +  # dynamic rent from user
    #         self.FIXED_BILL_AMOUNTS['water'] +
    #         self.FIXED_BILL_AMOUNTS['khala'] +
    #         self.FIXED_BILL_AMOUNTS['net'] +
    #         self.FIXED_BILL_AMOUNTS['current'] +
    #         self.FIXED_BILL_AMOUNTS['other']
    #     )
    #     elif self.bill_type == 'mess_rent':
    #         fixed_bill_total = self.user.seat_rent
    #     else:
    #         fixed_bill_total = self.FIXED_BILL_AMOUNTS.get(self.bill_type, 0.00)
    #     return fixed_bill_total + meal_bill
    
    def calculate_total_bill(self):
        year = self.due_date.year
        month = self.due_date.month
        meal_bill = Decimal(str(Bill.calculate_meal_bill(self.user, year, month)['total']))
        
        if self.bill_type == 'all_fixed':
            fixed_bill_total = (
                self.user.seat_rent +
                self.FIXED_BILL_AMOUNTS['water'] +
                self.FIXED_BILL_AMOUNTS['khala'] +
                self.FIXED_BILL_AMOUNTS['net'] +
                self.FIXED_BILL_AMOUNTS['current'] +
                self.FIXED_BILL_AMOUNTS['other']
            )
        elif self.bill_type == 'mess_rent':
            fixed_bill_total = self.user.seat_rent
        else:
            fixed_bill_total = self.FIXED_BILL_AMOUNTS.get(self.bill_type, Decimal('0.00'))
        return fixed_bill_total + meal_bill
    
    
    def save(self, *args, **kwargs):
        if self.status == 'Paid':
            existing_paid = Bill.objects.filter(
                user=self.user,
                due_date__year=self.due_date.year,
                due_date__month=self.due_date.month,
                status='Paid'
            ).exclude(pk=self.pk)
            if existing_paid.exists():
                raise ValidationError("This month's bill has already been paid.")

        self.total_amount = self.calculate_total_bill()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.total_amount} - {self.status}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"