from django.db import models
from django.utils import timezone
from students.models import Student

class FeeRecord(models.Model):
    FEE_TYPE_CHOICES = [
        ("Monthly", "Monthly Fee"),
        ("Annual", "Annual Fee"),
    ]
    STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Overdue", "Overdue"),
    ]

    payment_id = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_records")
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default="Monthly")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    pay_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    description = models.CharField(max_length=255, blank=True, help_text="e.g. June 2025 Hostel Fee")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_id:
            last = FeeRecord.objects.order_by("id").last()
            num = (last.id + 1) if last else 1
            self.payment_id = f"PAY{num:04d}"
        if self.status == "Paid" and not self.pay_date:
            self.pay_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id} - {self.student.name} ({self.fee_type}) - {self.status}"
