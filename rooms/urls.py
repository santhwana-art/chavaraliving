from django.urls import path
from . import views

urlpatterns = [
    path("rooms/", views.room_list, name="room_list"),
    path("rooms/add/", views.room_add, name="room_add"),
    path("rooms/<str:pk>/edit/", views.room_edit, name="room_edit"),
    path("rooms/<str:pk>/delete/", views.room_delete, name="room_delete"),
    path("rooms/allocate/", views.allocate_room, name="allocate_room"),
    path("rooms/bookings/", views.booking_list, name="booking_list"),
    path("rooms/bookings/<int:pk>/vacate/", views.vacate_room, name="vacate_room"),
]
