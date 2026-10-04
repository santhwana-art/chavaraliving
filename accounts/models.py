from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)

    def is_admin_user(self):
        return self.role == 'admin'

    def is_student_user(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class HostelSetting(models.Model):
    """Stores configurable hostel settings editable by the administrator."""
    hostel_name = models.CharField(max_length=150, default="Chavara Living")
    tagline = models.CharField(max_length=200, default="Smart Hostel Management System")
    phone = models.CharField(max_length=30, default="+91 98765 43210")
    email = models.EmailField(default="support@chavaraliving.in")
    address = models.CharField(max_length=255, default="Chavara Campus, Bangalore")
    emergency_contact = models.CharField(max_length=30, default="+91 98765 00000")
    rules_notice = models.TextField(blank=True, default="Hostel gate closes at 9:00 PM. Visitors allowed between 4:00 PM and 6:30 PM only.")
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(id=1)
        return setting

    def __str__(self):
        return self.hostel_name
