from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HostelSetting
from .forms import (
    LoginForm,
    StudentRegistrationForm,
    HostelSettingForm,
    AdminPasswordChangeForm,
)

def home_view(request):
    """Modern landing page for Chavara Living with real database statistics."""
    from students.models import Student
    from rooms.models import Room
    from mess.models import MessSubscription
    from leaves.models import LeaveRequest

    total_students = Student.objects.count()
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status="Occupied").count()
    active_mess = MessSubscription.objects.filter(status="Active").count()
    total_leaves = LeaveRequest.objects.count()

    context = {
        "total_students": total_students,
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "active_mess": active_mess,
        "total_leaves": total_leaves,
    }
    return render(request, "home.html", context)


def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("admin_dashboard")
        else:
            return redirect("student_dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if user.role == "admin":
                return redirect("admin_dashboard")
            else:
                return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("admin_dashboard")
        else:
            return redirect("student_dashboard")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user, student = form.save()
            login(request, user)
            messages.success(request, f"Registration complete! Welcome to Chavara Living, {student.name}. Your Student ID is {student.student_id}.")
            return redirect("student_dashboard")
        else:
            messages.error(request, "Please correct the highlighted errors below to complete registration.")
    else:
        form = StudentRegistrationForm()

    return render(request, "register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


@login_required
def admin_settings_view(request):
    """Admin settings page to configure hostel info and admin security."""
    if not request.user.is_authenticated or request.user.role != "admin":
        return redirect("login")

    setting = HostelSetting.get_settings()
    hostel_form = HostelSettingForm(instance=setting)
    password_form = AdminPasswordChangeForm(user=request.user)

    if request.method == "POST":
        action = request.POST.get("form_action")
        if action == "update_hostel":
            hostel_form = HostelSettingForm(request.POST, instance=setting)
            if hostel_form.is_valid():
                hostel_form.save()
                messages.success(request, "✓ Hostel settings (name, phone, email, address) updated successfully!")
                return redirect("admin_settings")
            else:
                messages.error(request, "Please check the hostel profile form for errors.")
        elif action == "update_password":
            password_form = AdminPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                new_pwd = password_form.cleaned_data["new_password"]
                request.user.set_password(new_pwd)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "✓ Password changed successfully! Session maintained securely.")
                return redirect("admin_settings")
            else:
                messages.error(request, "Please check the password fields below.")
        elif action == "update_admin_profile":
            name = request.POST.get("admin_name", "").strip()
            email = request.POST.get("admin_email", "").strip()
            phone = request.POST.get("admin_phone", "").strip()
            if name:
                request.user.first_name = name
            if email:
                request.user.email = email
            if phone:
                request.user.phone = phone
            request.user.save()
            messages.success(request, "✓ Administrator profile details updated successfully!")
            return redirect("admin_settings")

    return render(request, "admin_panel/settings.html", {
        "setting": setting,
        "hostel_form": hostel_form,
        "password_form": password_form,
    })
