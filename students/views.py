from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student
from .forms import StudentForm, StudentEditForm
from rooms.models import Booking
from fees.models import FeeRecord
from complaints.models import Complaint

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "admin":
            from django.shortcuts import redirect
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "student":
            from django.shortcuts import redirect
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

# ---- Admin Views ----

@login_required
@admin_required
def admin_dashboard(request):
    from rooms.models import Room, Booking
    total_students = Student.objects.count()
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status="Occupied").count()
    pending_payments = FeeRecord.objects.filter(status__in=["Pending","Overdue"]).count()
    active_complaints = Complaint.objects.filter(status__in=["Pending","In Progress"]).count()
    recent_students = Student.objects.order_by("-created_at")[:5]
    recent_complaints = Complaint.objects.order_by("-submission_date")[:5]
    recent_fees = FeeRecord.objects.order_by("-created_at")[:5]

    # Chart data: room type occupancy
    single_count = Room.objects.filter(room_type="Single").count()
    double_count = Room.objects.filter(room_type="Double").count()
    triple_count = Room.objects.filter(room_type="Triple").count()

    # Fee status chart
    paid_count = FeeRecord.objects.filter(status="Paid").count()
    pending_count = FeeRecord.objects.filter(status="Pending").count()
    overdue_count = FeeRecord.objects.filter(status="Overdue").count()

    # --- Popup modal data ---
    all_students = Student.objects.select_related("user").order_by("name")
    occupied_room_bookings = Booking.objects.filter(status="Active").select_related("student", "room").order_by("room__room_no")
    pending_fee_records = FeeRecord.objects.filter(status__in=["Pending", "Overdue"]).select_related("student").order_by("-due_date")
    active_complaint_list = Complaint.objects.filter(status__in=["Pending", "In Progress"]).select_related("student").order_by("-submission_date")

    # --- Chart popup data ---
    single_rooms = Room.objects.filter(room_type="Single").order_by("room_no")
    double_rooms = Room.objects.filter(room_type="Double").order_by("room_no")
    triple_rooms = Room.objects.filter(room_type="Triple").order_by("room_no")
    paid_fees = FeeRecord.objects.filter(status="Paid").select_related("student").order_by("-pay_date")[:15]
    pending_fees_list = FeeRecord.objects.filter(status="Pending").select_related("student").order_by("-due_date")[:15]
    overdue_fees = FeeRecord.objects.filter(status="Overdue").select_related("student").order_by("-due_date")[:15]

    # --- Mess subscription popup data ---
    try:
        from mess.models import MessSubscription
        active_mess_count = MessSubscription.objects.filter(status="Active").count()
        active_mess_subscribers = MessSubscription.objects.filter(status="Active").select_related("student").order_by("-start_date")
    except Exception:
        active_mess_count = 0
        active_mess_subscribers = []

    # --- Leave request data ---
    try:
        from leaves.models import LeaveRequest
        pending_leaves_count = LeaveRequest.objects.filter(status="Pending").count()
        pending_leaves_list = LeaveRequest.objects.filter(status="Pending").select_related("student").order_by("-applied_on")[:10]
    except Exception:
        pending_leaves_count = 0
        pending_leaves_list = []

    context = {
        "total_students": total_students,
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "pending_payments": pending_payments,
        "active_complaints": active_complaints,
        "active_mess_count": active_mess_count,
        "active_mess_subscribers": active_mess_subscribers,
        "pending_leaves_count": pending_leaves_count,
        "pending_leaves_list": pending_leaves_list,
        "recent_students": recent_students,
        "recent_complaints": recent_complaints,
        "recent_fees": recent_fees,
        "single_count": single_count,
        "double_count": double_count,
        "triple_count": triple_count,
        "paid_count": paid_count,
        "pending_count": pending_count,
        "overdue_count": overdue_count,
        # stat card popup data
        "all_students": all_students,
        "occupied_room_bookings": occupied_room_bookings,
        "pending_fee_records": pending_fee_records,
        "active_complaint_list": active_complaint_list,
        # chart popup data
        "single_rooms": single_rooms,
        "double_rooms": double_rooms,
        "triple_rooms": triple_rooms,
        "paid_fees": paid_fees,
        "pending_fees_list": pending_fees_list,
        "overdue_fees": overdue_fees,
    }
    return render(request, "admin_panel/dashboard.html", context)

@login_required
@admin_required
def student_list(request):
    query = request.GET.get("q", "")
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(name__icontains=query) | Q(student_id__icontains=query) |
            Q(contact__icontains=query) | Q(course__icontains=query)
        )
    return render(request, "admin_panel/students/list.html", {"students": students, "query": query})

@login_required
@admin_required
def student_add(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            # --- Optional initial fee record ---
            if request.POST.get("enable_fee_record"):
                fee_amount = request.POST.get("fee_amount", "").strip()
                fee_due_date = request.POST.get("fee_due_date", "").strip()
                fee_type = request.POST.get("fee_type", "Monthly").strip()
                fee_status = request.POST.get("fee_status", "Pending").strip()
                fee_description = request.POST.get("fee_description", "").strip()
                if fee_amount and fee_due_date:
                    from fees.models import FeeRecord
                    from django.utils import timezone
                    fee = FeeRecord(
                        student=student,
                        fee_type=fee_type,
                        amount=fee_amount,
                        due_date=fee_due_date,
                        status=fee_status,
                        description=fee_description,
                    )
                    if fee_status == "Paid":
                        fee.pay_date = timezone.now().date()
                    fee.save()
                    messages.success(request, f"Student registered and fee record ({fee.payment_id}) created.")
                else:
                    messages.success(request, "Student registered successfully. (Fee record skipped — amount or due date missing.)")
            else:
                messages.success(request, "Student registered successfully.")
            return redirect("student_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StudentForm()
    return render(request, "admin_panel/students/form.html", {"form": form, "action": "Register"})

@login_required
@admin_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect("student_list")
    else:
        form = StudentEditForm(instance=student)
    return render(request, "admin_panel/students/form.html", {"form": form, "action": "Edit", "student": student})

@login_required
@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.user.delete()  # cascades to student
        messages.success(request, "Student deleted.")
        return redirect("student_list")
    return render(request, "admin_panel/students/confirm_delete.html", {"student": student})

@login_required
@admin_required
def student_detail(request, pk):
    messages.warning(request, "Student Privacy Protection: Individual student personal details are confidential and restricted from administrator view.")
    return redirect("student_list")

# ---- Student Views ----

@login_required
@student_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    booking = Booking.objects.filter(student=student, status="Active").first()
    pending_fees = FeeRecord.objects.filter(student=student, status__in=["Pending","Overdue"]).count()
    total_fees = FeeRecord.objects.filter(student=student).count()
    active_complaints = Complaint.objects.filter(student=student, status__in=["Pending","In Progress"]).count()

    pending_fee_records = FeeRecord.objects.filter(student=student, status__in=["Pending","Overdue"]).order_by("due_date")
    all_fee_records = FeeRecord.objects.filter(student=student).order_by("-id")[:10]
    student_complaints = Complaint.objects.filter(student=student).order_by("-submission_date")[:10]
    roommates = Booking.objects.filter(room=booking.room, status="Active").exclude(student=student) if booking else []

    try:
        from mess.models import MessSubscription
        mess_sub = MessSubscription.objects.filter(student=student, status="Active").first()
    except Exception:
        mess_sub = None

    try:
        from leaves.models import LeaveRequest
        leaves_count = LeaveRequest.objects.filter(student=student).count()
        latest_leave = LeaveRequest.objects.filter(student=student).order_by("-applied_on").first()
    except Exception:
        leaves_count = 0
        latest_leave = None

    return render(request, "student_panel/dashboard.html", {
        "student": student,
        "booking": booking,
        "pending_fees": pending_fees,
        "total_fees": total_fees,
        "active_complaints": active_complaints,
        "pending_fee_records": pending_fee_records,
        "all_fee_records": all_fee_records,
        "student_complaints": student_complaints,
        "roommates": roommates,
        "mess_sub": mess_sub,
        "leaves_count": leaves_count,
        "latest_leave": latest_leave,
    })

@login_required
@student_required
def student_profile(request):
    from .forms import StudentSelfEditForm
    student = get_object_or_404(Student, user=request.user)
    booking = Booking.objects.filter(student=student, status="Active").first()

    if request.method == "POST":
        form = StudentSelfEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, "Your profile details have been saved successfully!")
            return redirect("student_profile")
        else:
            messages.error(request, "Please fix the highlighted errors below.")
    else:
        form = StudentSelfEditForm(instance=student)

    return render(request, "student_panel/profile.html", {
        "student": student,
        "booking": booking,
        "form": form,
    })
