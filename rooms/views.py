from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking
from .forms import RoomForm, BookingForm
from students.views import admin_required, student_required
from students.models import Student

@login_required
@admin_required
def room_list(request):
    rooms = Room.objects.all().order_by("room_no")
    return render(request, "admin_panel/rooms/list.html", {"rooms": rooms})

@login_required
@admin_required
def room_add(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Room added successfully.")
            return redirect("room_list")
    else:
        form = RoomForm()
    return render(request, "admin_panel/rooms/form.html", {"form": form, "action": "Add"})

@login_required
@admin_required
def room_edit(request, pk):
    room = get_object_or_404(Room, room_no=pk)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated.")
            return redirect("room_list")
    else:
        form = RoomForm(instance=room)
    return render(request, "admin_panel/rooms/form.html", {"form": form, "action": "Edit", "room": room})

@login_required
@admin_required
def room_delete(request, pk):
    room = get_object_or_404(Room, room_no=pk)
    if request.method == "POST":
        room.delete()
        messages.success(request, "Room deleted.")
        return redirect("room_list")
    return render(request, "admin_panel/rooms/confirm_delete.html", {"room": room})

@login_required
@admin_required
def allocate_room(request):
    import json
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data["student"]
            room = form.cleaned_data["room"]
            bed_number = form.cleaned_data.get("bed_number", 1)
            if room.is_full():
                messages.error(request, f"Room {room.room_no} is at full capacity.")
            elif Booking.objects.filter(student=student, status="Active").exists():
                messages.error(request, f"{student.name} already has an active room allocation.")
            else:
                form.save()
                messages.success(request, f"Room {room.room_no} (Bed #{bed_number}) allocated to {student.name}.")
                return redirect("booking_list")
        else:
            messages.error(request, "Please fix the errors in the allocation form.")
    else:
        form = BookingForm()

    available_rooms = Room.objects.filter(status="Available")
    unallocated_students = Student.objects.exclude(bookings__status="Active")
    rooms_info = {}
    for r in available_rooms:
        rooms_info[str(r.room_no)] = {
            "capacity": r.capacity,
            "room_type": r.room_type,
            "floor": r.floor,
            "occupied_beds": r.occupied_beds(),
            "available_beds": r.available_beds(),
        }

    return render(request, "admin_panel/rooms/allocate.html", {
        "form": form,
        "available_rooms": available_rooms,
        "unallocated_students": unallocated_students,
        "rooms_json": json.dumps(rooms_info),
    })

@login_required
@admin_required
def booking_list(request):
    bookings = Booking.objects.all().order_by("-created_at")
    return render(request, "admin_panel/rooms/bookings.html", {"bookings": bookings})

@login_required
@admin_required
def vacate_room(request, pk):
    booking = get_object_or_404(Booking, pk=pk, status="Active")
    if request.method == "POST":
        from django.utils import timezone
        booking.vacate_date = timezone.now().date()
        booking.status = "Vacated"
        booking.save()
        booking.room.update_status()
        messages.success(request, f"Room vacated for {booking.student.name}.")
        return redirect("booking_list")
    return render(request, "admin_panel/rooms/confirm_vacate.html", {"booking": booking})

# ---- Student Views ----
@login_required
@student_required
def student_room_view(request):
    student = get_object_or_404(Student, user=request.user)
    booking = Booking.objects.filter(student=student, status="Active").first()
    return render(request, "student_panel/room.html", {"booking": booking, "student": student})
