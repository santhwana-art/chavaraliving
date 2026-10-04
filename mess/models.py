from django.db import models
from django.utils import timezone
from students.models import Student


class MessSubscription(models.Model):
    PLAN_CHOICES = [
        ("30_days", "30 Days — ₹3,000"),
        ("15_days", "15 Days — ₹1,800"),
    ]
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Expired", "Expired"),
        ("Cancelled", "Cancelled"),
    ]

    subscription_id = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="mess_subscriptions")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.subscription_id:
            last = MessSubscription.objects.order_by("id").last()
            num = (last.id + 1) if last else 1
            self.subscription_id = f"MESS{num:04d}"
        # Auto-set amount based on plan
        if not self.amount:
            self.amount = 3000 if self.plan == "30_days" else 1800
        # Auto-set end_date
        if self.start_date and not self.end_date:
            days = 30 if self.plan == "30_days" else 15
            self.end_date = self.start_date + timezone.timedelta(days=days)
        super().save(*args, **kwargs)

    @property
    def days_remaining(self):
        if self.status != "Active":
            return 0
        delta = (self.end_date - timezone.now().date()).days
        return max(delta, 0)

    @property
    def is_expired(self):
        return timezone.now().date() > self.end_date

    def __str__(self):
        return f"{self.subscription_id} — {self.student.name} ({self.get_plan_display()})"
