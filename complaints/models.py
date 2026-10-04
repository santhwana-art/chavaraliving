from django.db import models
from students.models import Student

class Complaint(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    ]

    complaint_id = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="complaints")
    title = models.CharField(max_length=200)
    description = models.TextField()
    submission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    admin_notes = models.TextField(blank=True)
    resolved_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            last = Complaint.objects.order_by("id").last()
            num = (last.id + 1) if last else 1
            self.complaint_id = f"CP{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.complaint_id} - {self.student.name}: {self.title}"
