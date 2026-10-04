from django.db import models
from django.utils import timezone
from students.models import Student

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ("Home Visit", "Home Visit"),
        ("Semester Vacation", "Semester Vacation"),
        ("Medical Leave", "Medical / Sick Leave"),
        ("Academic / Internship", "Academic / Internship"),
        ("Family Emergency", "Family Emergency"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )
    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPES,
        default="Home Visit"
    )
    start_date = models.DateField(help_text="Start date of leave")
    end_date = models.DateField(help_text="End date of leave")
    reason = models.TextField(help_text="Detailed reason for leave request")
    parent_contact = models.CharField(
        max_length=20,
        help_text="Parent or Guardian emergency contact phone"
    )
    destination_city = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Destination / Home City during leave"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    admin_remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Remarks / reason from hostel admin"
    )
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-applied_on"]

    def __str__(self):
        return f"{self.student.name} — {self.leave_type} ({self.status})"

    @property
    def total_days(self):
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days
            return max(1, delta + 1)
        return 1

    @property
    def is_pending(self):
        return self.status == "Pending"

    @property
    def is_approved(self):
        return self.status == "Approved"

    @property
    def is_rejected(self):
        return self.status == "Rejected"
