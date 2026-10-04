from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["title","description"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control","placeholder":"Brief title of your complaint"}),
            "description": forms.Textarea(attrs={"class":"form-control","rows":5,"placeholder":"Describe your complaint in detail"}),
        }

class ComplaintResolveForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["status","admin_notes"]
        widgets = {
            "status": forms.Select(attrs={"class":"form-select"}),
            "admin_notes": forms.Textarea(attrs={"class":"form-control","rows":3,"placeholder":"Add notes or resolution details"}),
        }
