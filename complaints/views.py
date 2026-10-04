from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Complaint
from .forms import ComplaintForm, ComplaintResolveForm
from students.models import Student
from students.views import admin_required, student_required

@login_required
@admin_required
def complaint_list(request):
    status_filter = request.GET.get("status", "")
    complaints = Complaint.objects.all().order_by("-submission_date")
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    return render(request, "admin_panel/complaints/list.html", {
        "complaints": complaints, "status_filter": status_filter
    })

@login_required
@admin_required
def complaint_resolve(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == "POST":
        form = ComplaintResolveForm(request.POST, instance=complaint)
        if form.is_valid():
            c = form.save(commit=False)
            if c.status == "Resolved" and not c.resolved_date:
                c.resolved_date = timezone.now().date()
            c.save()
            messages.success(request, "Complaint updated.")
            return redirect("complaint_list")
    else:
        form = ComplaintResolveForm(instance=complaint)
    return render(request, "admin_panel/complaints/resolve.html", {"form": form, "complaint": complaint})

# ---- Student Views ----
@login_required
@student_required
def student_complaint_list(request):
    student = get_object_or_404(Student, user=request.user)
    complaints = Complaint.objects.filter(student=student).order_by("-submission_date")
    return render(request, "student_panel/complaints/list.html", {"complaints": complaints, "student": student})

@login_required
@student_required
def student_complaint_add(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = student
            complaint.save()
            messages.success(request, "Complaint submitted successfully.")
            return redirect("student_complaint_list")
    else:
        form = ComplaintForm()
    return render(request, "student_panel/complaints/form.html", {"form": form, "student": student})
