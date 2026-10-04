from django.urls import path
from rooms import views

urlpatterns = [
    path("room/", views.student_room_view, name="student_room"),
]
