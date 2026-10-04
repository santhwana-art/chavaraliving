from django import forms
from .models import MessSubscription


class MessSubscribeForm(forms.Form):
    """Form for students to subscribe to a mess plan."""
    PLAN_CHOICES = [
        ("30_days", "30 Days Plan — ₹3,000"),
        ("15_days", "15 Days Plan — ₹1,800"),
    ]
    plan = forms.ChoiceField(
        choices=PLAN_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "mess-plan-radio"}),
        label="Select Your Plan",
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control-custom",
        }),
        label="Subscription Start Date",
    )
