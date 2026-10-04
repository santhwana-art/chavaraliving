from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ("Single", "Single Occupancy (Max 1 Bed)"),
        ("Double", "Double Occupancy (Max 2 Beds)"),
        ("Triple", "Triple Occupancy (Max 3 Beds)"),
    ]
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Occupied", "Occupied"),
        ("Maintenance", "Under Maintenance"),
    ]

    room_no = models.CharField(max_length=20, unique=True, primary_key=True)
    capacity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Bed capacity (Single: max 1, Double: max 2, Triple: max 3)"
    )
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default="Single")
    floor = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Floor number (0 for Ground Floor, cannot be negative)"
    )
    block = models.CharField(max_length=50, default="Main Block")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")

    def clean(self):
        super().clean()
        if self.floor is not None and self.floor < 0:
            raise ValidationError({'floor': 'Floor number cannot be negative (0 or higher required).'})

        max_capacity_map = {
            "Single": 1,
            "Double": 2,
            "Triple": 3,
        }
        max_allowed = max_capacity_map.get(self.room_type, 3)

        if self.capacity is not None:
            if self.capacity < 1:
                raise ValidationError({'capacity': 'Bed capacity must be at least 1 (cannot be negative or zero).'})
            if self.capacity > max_allowed:
                raise ValidationError({
                    'capacity': f'For {self.room_type} sharing, maximum allowed bed capacity is {max_allowed}.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def current_occupancy(self):
        return self.bookings.filter(status="Active").count()

    def occupied_beds(self):
        return list(self.bookings.filter(status="Active").values_list("bed_number", flat=True))

    def available_beds(self):
        occupied = set(self.occupied_beds())
        return [b for b in range(1, self.capacity + 1) if b not in occupied]

    def is_full(self):
        return self.current_occupancy() >= self.capacity

    def update_status(self):
        if self.current_occupancy() >= self.capacity:
            self.status = "Occupied"
        elif self.current_occupancy() > 0:
            self.status = "Available"
        else:
            self.status = "Available"
        self.save()

    def __str__(self):
        return f"Room {self.room_no} ({self.room_type}, Floor {self.floor})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Transferred", "Transferred"),
        ("Vacated", "Vacated"),
    ]

    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    bed_number = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Bed number (must be >= 1 and <= room capacity)"
    )
    arrival_date = models.DateField()
    vacate_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.bed_number is not None and self.bed_number < 1:
            raise ValidationError({'bed_number': 'Bed number must be 1 or higher (cannot be negative or zero).'})

        if self.room_id:
            room = self.room
            if self.bed_number is not None and self.bed_number > room.capacity:
                raise ValidationError({
                    'bed_number': f'Bed number {self.bed_number} exceeds Room {room.room_no} capacity of {room.capacity} bed(s).'
                })
            # Check if this bed is already taken by another active booking
            conflict = Booking.objects.filter(
                room=room,
                bed_number=self.bed_number,
                status="Active"
            )
            if self.pk:
                conflict = conflict.exclude(pk=self.pk)
            if conflict.exists():
                raise ValidationError({
                    'bed_number': f'Bed #{self.bed_number} in Room {room.room_no} is already assigned to an active resident.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.booking_id:
            last = Booking.objects.order_by("id").last()
            num = (last.id + 1) if last else 1
            self.booking_id = f"BK{num:04d}"
        super().save(*args, **kwargs)
        self.room.update_status()

    def __str__(self):
        return f"{self.booking_id} - {self.student.name} -> Room {self.room.room_no} (Bed #{self.bed_number})"
