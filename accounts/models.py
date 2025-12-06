from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# -----------------------
# Custom User Manager
# -----------------------
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, role='patient', **extra_fields):
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, role='admin', **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, role, **extra_fields)


# -----------------------
# Custom User Model
# -----------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('provider', 'Healthcare Provider'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')

    # for providers only
    designation = models.CharField(max_length=100, blank=True, null=True)

    objects = UserManager()

    # Helpers
    def is_patient(self):
        return self.role == "patient"

    def is_provider(self):
        return self.role == "provider"

    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        # show full name if available
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username


# -----------------------
# Appointment Model
# -----------------------
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('reschedule_requested', 'Reschedule Requested'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_made")
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_received")

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    reason = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.patient.first_name} {self.patient.last_name} → "
            f"{self.provider.first_name} {self.provider.last_name} "
            f"on {self.date}"
        )
