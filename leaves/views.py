from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import LeaveRequest
from .forms import StudentLeaveForm
from students.models import Student

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "admin":
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "student":
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ════════════════════════════════
#          ADMIN VIEWS
# ════════════════════════════════

@login_required
@admin_required
def admin_leave_list(request):
    """Admin view to review and manage all student leave requests."""
    status_filter = request.GET.get("status", "all")
    queryset = LeaveRequest.objects.select_related("student", "student__user")

    if status_filter in ["Pending", "Approved", "Rejected"]:
        queryset = queryset.filter(status=status_filter)

    leaves = queryset.order_by("-applied_on")

    total_pending = LeaveRequest.objects.filter(status="Pending").count()
    total_approved = LeaveRequest.objects.filter(status="Approved").count()
    total_rejected = LeaveRequest.objects.filter(status="Rejected").count()
    total_all = LeaveRequest.objects.count()

    context = {
        "leaves": leaves,
        "status_filter": status_filter,
        "total_pending": total_pending,
        "total_approved": total_approved,
        "total_rejected": total_rejected,
        "total_all": total_all,
    }
    return render(request, "admin_panel/leaves/list.html", context)


@login_required
@admin_required
def admin_leave_action(request, leave_id):
    """Approve or Reject a student's leave request."""
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    if request.method == "POST":
        action = request.POST.get("action")
        remarks = request.POST.get("remarks", "").strip()

        if action == "approve":
            leave.status = "Approved"
            leave.admin_remarks = remarks or "Leave request approved by hostel warden."
            leave.reviewed_on = timezone.now()
            leave.save()
            messages.success(request, f"✓ Leave request for {leave.student.name} approved successfully.")
        elif action == "reject":
            leave.status = "Rejected"
            leave.admin_remarks = remarks or "Leave request declined by hostel warden."
            leave.reviewed_on = timezone.now()
            leave.save()
            messages.warning(request, f"✗ Leave request for {leave.student.name} was rejected.")
        else:
            messages.error(request, "Invalid action requested.")

    return redirect("admin_leave_list")


# ════════════════════════════════
#         STUDENT VIEWS
# ════════════════════════════════

@login_required
@student_required
def student_leave_list(request):
    """Student view to see their own leave requests and status."""
    student = get_object_or_404(Student, user=request.user)
    leaves = LeaveRequest.objects.filter(student=student).order_by("-applied_on")

    pending_count = leaves.filter(status="Pending").count()
    approved_count = leaves.filter(status="Approved").count()

    return render(request, "student_panel/leaves/list.html", {
        "student": student,
        "leaves": leaves,
        "pending_count": pending_count,
        "approved_count": approved_count,
    })


@login_required
@student_required
def student_leave_apply(request):
    """Student view to apply for hostel leave."""
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = StudentLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.student = student
            leave.status = "Pending"
            leave.save()
            messages.success(request, f"🎉 Leave application submitted successfully for {leave.total_days} day(s)! Waiting for admin approval.")
            return redirect("student_leave_list")
        else:
            messages.error(request, "Please fix the highlighted errors in your leave application.")
    else:
        # Pre-fill parent contact if available on student model
        initial_data = {}
        if hasattr(student, "parent_phone") and student.parent_phone:
            initial_data["parent_contact"] = student.parent_phone
        elif student.contact:
            initial_data["parent_contact"] = student.contact
        form = StudentLeaveForm(initial=initial_data)

    return render(request, "student_panel/leaves/apply.html", {
        "student": student,
        "form": form,
    })


@login_required
@student_required
def student_leave_cancel(request, leave_id):
    """Allow student to cancel a pending leave request."""
    student = get_object_or_404(Student, user=request.user)
    leave = get_object_or_404(LeaveRequest, pk=leave_id, student=student)

    if leave.status != "Pending":
        messages.warning(request, "Only pending leave requests can be cancelled.")
        return redirect("student_leave_list")

    if request.method == "POST":
        leave.status = "Cancelled"
        leave.admin_remarks = "Cancelled by student."
        leave.save()
        messages.success(request, "Your leave request has been cancelled.")

    return redirect("student_leave_list")
