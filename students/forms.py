from django import forms
from .models import Student
from accounts.models import CustomUser

class StudentForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username for login",
            "autocomplete": "off",
            "readonly": "readonly",
            "onfocus": "this.removeAttribute('readonly');"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "id": "studentPasswordInput",
            "autocomplete": "new-password",
            "readonly": "readonly",
            "onfocus": "this.removeAttribute('readonly');"
        })
    )

    class Meta:
        model = Student
        fields = ["name", "contact", "email", "course", "year", "address", "date_of_admission"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Student Full Name", "autocomplete": "off"}),
            "contact": forms.TextInput(attrs={"class": "form-control", "placeholder": "10-digit mobile number", "maxlength": "10", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com", "autocomplete": "off"}),
            "course": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. B.Tech Computer Science", "autocomplete": "off"}),
            "year": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Permanent Address", "autocomplete": "off"}),
            "date_of_admission": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password", "")
        from accounts.forms import validate_password_rules
        errors = validate_password_rules(pwd)
        if errors:
            raise forms.ValidationError(" ".join(errors))
        return pwd

    def clean_contact(self):
        contact = self.cleaned_data.get("contact", "").strip()
        if not contact.isdigit():
            raise forms.ValidationError("Phone number must contain only numeric digits.")
        if len(contact) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return contact

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            email=self.cleaned_data["email"],
            phone=self.cleaned_data["contact"],
            role="student",
        )
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
        return student

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "contact", "email", "course", "year", "address", "date_of_admission"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "contact": forms.TextInput(attrs={"class": "form-control", "maxlength": "10", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "course": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "year": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "autocomplete": "off"}),
            "date_of_admission": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean_contact(self):
        contact = self.cleaned_data.get("contact", "").strip()
        if not contact.isdigit():
            raise forms.ValidationError("Phone number must contain only numeric digits.")
        if len(contact) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return contact

    def save(self, commit=True):
        student = super().save(commit=commit)
        if student.user:
            student.user.phone = student.contact
            student.user.email = student.email
            student.user.save()
        return student


class StudentSelfEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Leave blank to keep existing password",
            "id": "selfNewPassword",
            "autocomplete": "new-password"
        })
    )
    confirm_new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password",
            "id": "selfConfirmNewPassword",
            "autocomplete": "new-password"
        })
    )

    class Meta:
        model = Student
        fields = ["name", "contact", "email", "course", "year", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}),
            "contact": forms.TextInput(attrs={"class": "form-control", "maxlength": "10", "placeholder": "10-digit mobile"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "course": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. B.Tech Computer Science"}),
            "year": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Permanent residential address"}),
        }

    def clean_contact(self):
        contact = self.cleaned_data.get("contact", "").strip()
        if not contact.isdigit():
            raise forms.ValidationError("Phone number must contain only numeric digits.")
        if len(contact) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return contact

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        from accounts.models import CustomUser
        user_conflict = CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.user.pk).exists()
        student_conflict = Student.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        if user_conflict or student_conflict:
            raise forms.ValidationError("This email address is already in use by another account.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        new_pwd = cleaned_data.get("new_password")
        confirm_pwd = cleaned_data.get("confirm_new_password")

        if new_pwd or confirm_pwd:
            if new_pwd != confirm_pwd:
                self.add_error("confirm_new_password", "New passwords do not match.")
            from accounts.forms import validate_password_rules
            errors = validate_password_rules(new_pwd)
            if errors:
                self.add_error("new_password", " ".join(errors))
        return cleaned_data

    def save(self, request=None, commit=True):
        student = super().save(commit=commit)
        user = student.user
        if user:
            user.first_name = student.name
            user.email = student.email
            user.phone = student.contact
            new_pwd = self.cleaned_data.get("new_password")
            if new_pwd:
                user.set_password(new_pwd)
            user.save()
            if new_pwd and request:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
        return student
