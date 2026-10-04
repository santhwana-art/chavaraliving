from django import forms
from .models import FeeRecord
from students.models import Student

class FeeForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={"class":"form-select"})
    )
    class Meta:
        model = FeeRecord
        fields = ["student","fee_type","amount","due_date","pay_date","status","description"]
        widgets = {
            "fee_type": forms.Select(attrs={"class":"form-select"}),
            "amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "due_date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "pay_date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "status": forms.Select(attrs={"class":"form-select"}),
            "description": forms.TextInput(attrs={"class":"form-control","placeholder":"e.g. October 2025 Hostel Fee"}),
        }
