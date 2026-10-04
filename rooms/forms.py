from django import forms
from .models import Room, Booking
from students.models import Student

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["room_no", "room_type", "capacity", "floor", "block", "status"]
        widgets = {
            "room_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 101, 202"}),
            "room_type": forms.Select(attrs={"class": "form-select", "id": "id_room_type", "onchange": "updateCapacityLimit(this.value)"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "id": "id_capacity", "min": "1", "max": "3", "placeholder": "Beds (1-3)"}),
            "floor": forms.NumberInput(attrs={"class": "form-control", "id": "id_floor", "min": "0", "placeholder": "Floor (0 for Ground)"}),
            "block": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Block A, Main Wing"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_floor(self):
        floor = self.cleaned_data.get("floor")
        if floor is not None and floor < 0:
            raise forms.ValidationError("Floor number cannot be negative (0 or higher required).")
        return floor

    def clean_capacity(self):
        capacity = self.cleaned_data.get("capacity")
        if capacity is not None and capacity < 1:
            raise forms.ValidationError("Bed capacity must be at least 1 (cannot be negative or zero).")
        return capacity

    def clean(self):
        cleaned_data = super().clean()
        room_type = cleaned_data.get("room_type")
        capacity = cleaned_data.get("capacity")

        max_map = {
            "Single": 1,
            "Double": 2,
            "Triple": 3,
        }
        if room_type in max_map and capacity is not None:
            max_allowed = max_map[room_type]
            if capacity > max_allowed:
                self.add_error("capacity", f"For {room_type} sharing, max bed capacity is {max_allowed}.")
            elif capacity < 1:
                self.add_error("capacity", "Bed capacity must be at least 1.")
        return cleaned_data


class BookingForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.none(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_student"})
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_room", "onchange": "onRoomSelected(this.value)"})
    )
    bed_number = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "id": "id_bed_number",
            "min": "1",
            "placeholder": "Enter bed number (e.g. 1)"
        }),
        help_text="Bed number must be 1 or higher, within the room's capacity"
    )

    class Meta:
        model = Booking
        fields = ["student", "room", "bed_number", "arrival_date"]
        widgets = {
            "arrival_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show students who DO NOT have an active room allocation
        self.fields["student"].queryset = Student.objects.exclude(bookings__status="Active").order_by("student_id")
        # Only show rooms that have available beds
        self.fields["room"].queryset = Room.objects.filter(status="Available").order_by("room_no")

    def clean_bed_number(self):
        bed_number = self.cleaned_data.get("bed_number")
        if bed_number is not None and bed_number < 1:
            raise forms.ValidationError("Bed number cannot be negative or zero (must be 1 or greater).")
        return bed_number

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        bed_number = cleaned_data.get("bed_number")

        if room and bed_number:
            if bed_number > room.capacity:
                self.add_error("bed_number", f"Room {room.room_no} only has {room.capacity} bed(s). Bed #{bed_number} is not valid.")
            else:
                conflict = Booking.objects.filter(room=room, bed_number=bed_number, status="Active")
                if self.instance and self.instance.pk:
                    conflict = conflict.exclude(pk=self.instance.pk)
                if conflict.exists():
                    self.add_error("bed_number", f"Bed #{bed_number} in Room {room.room_no} is already occupied.")
        return cleaned_data
