from django.contrib import admin  # type: ignore
from .models import Room, Booking

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_no', 'room_type', 'capacity', 'floor', 'block', 'status')
    list_filter = ('room_type', 'status', 'floor', 'block')
    search_fields = ('room_no', 'block')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'student', 'room', 'arrival_date', 'vacate_date', 'status')
    list_filter = ('status', 'arrival_date')
    search_fields = ('booking_id', 'student__name', 'room__room_no')
    readonly_fields = ('booking_id', 'created_at')
