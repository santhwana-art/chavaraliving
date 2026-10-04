from django import forms
from django.utils import timezone
from .models import LeaveRequest

class StudentLeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "parent_contact", "destination_city", "reason"]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-select", "id": "id_leave_type"}),
            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "id": "id_start_date",
                "placeholder": "Select departure date"
            }),
            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "id": "id_end_date",
                "placeholder": "Select return date"
            }),
            "parent_contact": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Parent/Guardian phone (e.g. 9876543210)",
                "id": "id_parent_contact"
            }),
            "destination_city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Cochin, Kerala",
                "id": "id_destination_city"
            }),
            "reason": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Provide detailed reason for your leave request...",
                "id": "id_reason"
            }),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        today = timezone.now().date()
        if start_date and start_date < today:
            raise forms.ValidationError("Leave departure date cannot be in the past.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        contact = cleaned_data.get("parent_contact", "")

        if start and end:
            if end < start:
                self.add_error("end_date", "Return date cannot be earlier than departure date.")

        if contact:
            digits = "".join(filter(str.isdigit, contact))
            if len(digits) < 10:
                self.add_error("parent_contact", "Please provide a valid phone number with at least 10 digits.")

        return cleaned_data
