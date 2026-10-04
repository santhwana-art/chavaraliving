from django.contrib import admin  # type: ignore
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'student', 'title', 'status', 'submission_date', 'resolved_date')
    list_filter = ('status', 'submission_date')
    search_fields = ('complaint_id', 'student__name', 'title', 'description')
    readonly_fields = ('complaint_id', 'submission_date')
