import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from accounts.models import CustomUser
from students.models import Student, phone_validator

def validate_password_rules(password):
    """Validates that password has min 8 chars, 1 uppercase, and 1 special character."""
    errors = []
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password or ""):
        errors.append("Password must contain at least 1 uppercase letter (A-Z).")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+[\]\\/]', password or ""):
        errors.append("Password must contain at least 1 special character (e.g. !@#$%^&*).")
    return errors


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'id': 'id_username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'passwordInput',
            'autocomplete': 'current-password'
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        return password


class StudentRegistrationForm(forms.Form):
    YEAR_CHOICES = [
        (1, "1st Year"),
        (2, "2nd Year"),
        (3, "3rd Year"),
        (4, "4th Year"),
        (5, "5th Year"),
    ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name (e.g. Alex Johnson)',
            'autocomplete': 'name',
            'required': 'required'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose username (e.g. alexj)',
            'autocomplete': 'username',
            'required': 'required'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'student@example.com',
            'autocomplete': 'email',
            'required': 'required'
        })
    )
    contact = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile number',
            'maxlength': '10',
            'autocomplete': 'tel',
            'required': 'required'
        })
    )
    course = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. B.Tech Computer Science / BCA',
            'required': 'required'
        })
    )
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a secure password',
            'id': 'regPasswordInput',
            'autocomplete': 'new-password',
            'required': 'required'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'regConfirmPasswordInput',
            'autocomplete': 'new-password',
            'required': 'required'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Permanent residential address (optional)'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists() or Student.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_contact(self):
        contact = self.cleaned_data.get("contact", "").strip()
        if not contact.isdigit():
            raise forms.ValidationError("Mobile number must contain digits only.")
        if len(contact) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return contact

    def clean_password(self):
        pwd = self.cleaned_data.get("password", "")
        errors = validate_password_rules(pwd)
        if errors:
            raise forms.ValidationError(" ".join(errors))
        return pwd

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            phone=self.cleaned_data["contact"],
            role="student"
        )
        student = Student.objects.create(
            user=user,
            name=self.cleaned_data["name"],
            contact=self.cleaned_data["contact"],
            email=self.cleaned_data["email"],
            course=self.cleaned_data["course"],
            year=int(self.cleaned_data["year"]),
            address=self.cleaned_data.get("address", ""),
            date_of_admission=timezone.now().date()
        )
        return user, student


class HostelSettingForm(forms.ModelForm):
    class Meta:
        from .models import HostelSetting
        model = HostelSetting
        fields = [
            "hostel_name",
            "tagline",
            "phone",
            "email",
            "address",
            "emergency_contact",
            "rules_notice",
        ]
        widgets = {
            "hostel_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Chavara Living"}),
            "tagline": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Smart Hostel Management System"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 98765 43210"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contact@chavaraliving.in"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Campus address, City"}),
            "emergency_contact": forms.TextInput(attrs={"class": "form-control", "placeholder": "Warden emergency phone"}),
            "rules_notice": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Hostel notices & gate timings..."}),
        }


class AdminPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter your current password"}),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new secure password"}),
        label="New Password"
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new secure password"}),
        label="Confirm New Password"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        cur = self.cleaned_data.get("current_password")
        if not self.user.check_password(cur):
            raise forms.ValidationError("Current password is not correct.")
        return cur

    def clean_new_password(self):
        new_pwd = self.cleaned_data.get("new_password")
        errors = validate_password_rules(new_pwd)
        if errors:
            raise forms.ValidationError(" ".join(errors))
        return new_pwd

    def clean(self):
        cleaned_data = super().clean()
        new_pwd = cleaned_data.get("new_password")
        confirm_pwd = cleaned_data.get("confirm_new_password")
        if new_pwd and confirm_pwd and new_pwd != confirm_pwd:
            self.add_error("confirm_new_password", "New passwords do not match.")
        return cleaned_data

