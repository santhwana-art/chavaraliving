from django.db import models
from django.core.validators import RegexValidator
from accounts.models import CustomUser

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Phone number must be exactly 10 numeric digits.'
)

class Student(models.Model):
    YEAR_CHOICES = [
        (1, "1st Year"),
        (2, "2nd Year"),
        (3, "3rd Year"),
        (4, "4th Year"),
        (5, "5th Year"),
    ]

    student_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_profile")
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=10, validators=[phone_validator])
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=100)
    year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    address = models.TextField(blank=True)
    date_of_admission = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            last = Student.objects.order_by("id").last()
            num = (last.id + 1) if last else 1
            self.student_id = f"CL{num:04d}"
        super().save(*args, **kwargs)
        if self.user and self.user.phone != self.contact:
            self.user.phone = self.contact
            self.user.save(update_fields=["phone"])

    def get_room(self):
        from rooms.models import Booking
        booking = Booking.objects.filter(student=self, status="Active").first()
        return booking.room if booking else None

    def __str__(self):
        return f"{self.student_id} - {self.name}"
