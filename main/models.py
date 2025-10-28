from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
from uuid import uuid4
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    student_id = models.CharField(max_length=255, blank=True, null=True)  # Student ID
    faculty = models.CharField(max_length=255, blank=True, null=True)  # Faculty
    department = models.CharField(max_length=255, blank=True, null=True)  # Department
    student_category = models.CharField(max_length=50, choices=[
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('masters', 'Masters'),
        ('phd', 'PhD'),
        ('none', 'None'),
    ], blank=True, null=True)  # Student Category (Undergraduate, Postgraduate, etc.)
    staff_category = models.CharField(max_length=50, choices=[
        ('librarian', 'Librarian'),
        ('member', 'Memeber'),
        ('staff', 'Staff'),
        ('donator', 'Donator'),
        ('none', 'None')
    ], blank=True, null=True)  # Student Category (Undergraduate, Postgraduate, etc.)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone', 'student_id', 'faculty', 'department', 'student_category', 'is_active', 'is_staff', 'is_superuser']  

    objects = UserManager()

    def __str__(self):
        return self.username

class Attendace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    METHOD_CHOICES = [
        ('thumbprint', 'Thumbprint'),
        ('manual', 'Manual'),
        ('id_card', 'ID Card'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    fingerprint_data = models.TextField()  # Store as base64 or binary
    reg_no = models.CharField(max_length=255, blank=True, null=True)  # Registration Number
    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    faculty = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    items = models.TextField(blank=True, null=True)  # Items brought by the user
    purpose = models.CharField(max_length=255, blank=True, null=True)  # Purpose of visit
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='manual')
    check_out = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_manage_attendance", "Can manage all attendance records"),
        ]

    def __str__(self):
        user_part = self.user.username if self.user else (self.name or self.reg_no or 'anonymous')
        return f"{user_part} - {self.fp_id or self.id}"

class Catalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    # Standardized catalogue record for MARC21, Dublin Core, AI tagging, etc.
    marc_tag = models.TextField(blank=True, null=True)
    dublin_core = models.TextField(blank=True, null=True)
    ai_suggestion = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=30, blank=True, null=True)
    issn = models.CharField(max_length=30, blank=True, null=True)
    lccn = models.CharField(max_length=30, blank=True, null=True)  # Library of Congress Control Number
    dewey_decimal = models.CharField(max_length=30, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    format = models.CharField(max_length=50, blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    contributors = models.TextField(blank=True, null=True)  # Authors, editors, etc.
    notes = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # For AI/ML tagging, keywords
    quantity = models.PositiveIntegerField(default=1, help_text="Number of copies available")
    can_be_borrowed = models.BooleanField(default=True, help_text="Can this catalog item be borrowed?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("can_manage_catalog", "Can manage all catalog records"),
        ]

    def __str__(self):
        return f"Catalog record for {self.title or self.subject or str(self.id)}"


class Circulation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('reserve', 'Reserve'),
    ]

    book = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name='circulations')
    student_name = models.CharField(max_length=255, blank=True, null=True, help_text="Student name")
    student_card_id = models.CharField(max_length=255, blank=True, null=True, help_text="Student card ID")
    borrow_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    actual_return = models.DateField(blank=True, null=True)
    fine = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')

    class Meta:
        permissions = [
            ("can_manage_circulation", "Can manage all circulation records"),
        ]

    def save(self, *args, **kwargs):
        # Only allow borrowing if available_count > 0 and can_be_borrowed is True
        if self.status == 'borrowed':
            if not self.book.can_be_borrowed:
                raise ValueError('This item cannot be borrowed.')
            available = self.book.available_count()
            if available <= 0:
                raise ValueError('No available copies to borrow.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} -> {self.user.username} ({self.status})"

class Acquisition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    SOURCE_CHOICES = [
        ('purchase', 'Purchase'),
        ('donation', 'Donation'),
        ('exchange', 'Exchange'),
    ]
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_acquired = models.DateField()
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acquisitions')

    class Meta:
        permissions = [
            ("can_manage_acquisition", "Can manage all acquisition records"),
        ]

    def __str__(self):
        return f"{self.title} ({self.source})"

class Duty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duties')
    date = models.DateField()
    shift = models.CharField(max_length=50)  # e.g., Morning, Afternoon, Evening
    notes = models.TextField(blank=True, null=True)

    class Meta:
        permissions = [
            ("can_manage_duty", "Can manage all duty records"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.shift})"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store_sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store_received_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    # read = models.BooleanField(default=False)  # Commented out: use API filtering only

    class Meta:
        permissions = [
            ("can_manage_messages", "Can manage all messages"),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.sent_at}"


