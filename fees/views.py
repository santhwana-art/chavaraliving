from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import FeeRecord
from .forms import FeeForm
from students.models import Student
from students.views import admin_required, student_required

@login_required
@admin_required
def fee_list(request):
    query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")
    sort_by = request.GET.get("sort", "due_date")
    sort_dir = request.GET.get("dir", "desc")

    ALLOWED_SORTS = {
        "payment_id": "payment_id",
        "student": "student__name",
        "amount": "amount",
        "due_date": "due_date",
        "pay_date": "pay_date",
        "status": "status",
    }
    sort_field = ALLOWED_SORTS.get(sort_by, "due_date")
    if sort_dir == "asc":
        fees = FeeRecord.objects.all().order_by(sort_field)
    else:
        fees = FeeRecord.objects.all().order_by(f"-{sort_field}")

    if query:
        fees = fees.filter(
            Q(student__name__icontains=query) | Q(student__student_id__icontains=query) |
            Q(payment_id__icontains=query)
        )
    if status_filter:
        fees = fees.filter(status=status_filter)
    return render(request, "admin_panel/fees/list.html", {
        "fees": fees, "query": query, "status_filter": status_filter,
        "sort_by": sort_by, "sort_dir": sort_dir,
    })

@login_required
@admin_required
def fee_add(request):
    if request.method == "POST":
        form = FeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee record created.")
            return redirect("fee_list")
    else:
        form = FeeForm()
    return render(request, "admin_panel/fees/form.html", {"form": form, "action": "Create"})

@login_required
@admin_required
def fee_edit(request, pk):
    fee = get_object_or_404(FeeRecord, pk=pk)
    if request.method == "POST":
        form = FeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee record updated.")
            return redirect("fee_list")
    else:
        form = FeeForm(instance=fee)
    return render(request, "admin_panel/fees/form.html", {"form": form, "action": "Edit", "fee": fee})

@login_required
@admin_required
def fee_delete(request, pk):
    fee = get_object_or_404(FeeRecord, pk=pk)
    if request.method == "POST":
        fee.delete()
        messages.success(request, "Fee record deleted.")
        return redirect("fee_list")
    return render(request, "admin_panel/fees/confirm_delete.html", {"fee": fee})

# ---- Student Views ----
@login_required
@student_required
def student_fee_list(request):
    student = get_object_or_404(Student, user=request.user)
    fees = FeeRecord.objects.filter(student=student).order_by("-due_date")
    return render(request, "student_panel/fees/list.html", {"fees": fees, "student": student})
