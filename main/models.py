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
    barcode = models.CharField(max_length=255, unique=True, null=True, blank=True)
    user_category = models.CharField(max_length=50, choices=[
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('alumnus', 'Alumnus'),
        ('others', 'Others'),
    ], blank=True, null=True)  # Student Category (Undergraduate, Postgraduate, etc.)
    staff_category = models.CharField(max_length=50, choices=[
        ('librarian', 'Librarian'),
        ('member', 'Memeber'),
        ('staff', 'Staff'),
        ('donator', 'Donator'),
        ('none', 'None')
    ], blank=True, null=True)  # Student Category (Undergraduate, Postgraduate, etc.)
    role = models.CharField(max_length=50, blank=True, null=True, help_text="User role (admin, staff, student, etc.)")
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone', 'student_id', 'faculty', 'department', 'user_category', 'staff_category', 'is_active', 'is_staff', 'is_superuser', 'barcode']  

    objects = UserManager()

    def __str__(self):
        return self.username
 

class Attendance(models.Model):
    SIGN_CHOICES = [
        ("signin", "Sign In"),
        ("signout", "Sign Out"),
        ("other", "Other"),  # optional
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    items = models.CharField(max_length=255, blank=True, null=True)
    method = models.CharField(max_length=50, default="barcode")

    # ✅ NEW FIELD (Sign in / Sign out)
    sign_type = models.CharField(
        max_length=20,
        choices=SIGN_CHOICES,
        default="signout"   # your default
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_manage_attendance", "Can manage all attendance records"),
        ]
        ordering = ['-created_at']
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.user.username} ({self.sign_type} at {self.created_at})"

class Catalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    barcode = models.CharField(max_length=255, unique=True, null=True, blank=True)
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
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowers', null=True)
    borrow_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    actual_return = models.DateField(blank=True, null=True)
    fine = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')

    class Meta:
        permissions = [
            ("can_manage_circulation", "Can manage all circulation records"),
        ]


    def __str__(self):
        return f"{self.book.title} -> {self.borrower.email} ({self.status})"

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


