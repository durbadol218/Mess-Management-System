from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models
from .constants import USER_TYPE
import random, string

def generate_registration_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class User_Model(AbstractUser):
    reg_no = models.CharField(max_length=100, unique=True, default=generate_registration_number, validators=[RegexValidator(r'^[A-Za-z0-9]+$', 'Invalid registration number')], blank=True, null=True)
    full_name = models.CharField(max_length=255,unique=True)
    email = models.EmailField(max_length=50,unique=True)
    education_details = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15,unique=True,validators=[RegexValidator(r'^\+?\d{10,15}$', 'Invalid contact number')])
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    is_approved = models.BooleanField(default=False)
    # joined_date = models.DateField(auto_now_add=True)
    # address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # profile_image = models.ImageField(upload_to='student_profiles/', blank=True, null=True)


    groups = models.ManyToManyField(Group, related_name="student_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="student_permissions", blank=True)


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
    