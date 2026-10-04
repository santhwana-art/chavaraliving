from django.urls import path
from . import views

# Student-side mess URLs — prefix: student/
urlpatterns = [
    path("mess/", views.student_mess_menu, name="student_mess_menu"),
    path("mess/subscribe/", views.student_mess_subscribe, name="student_mess_subscribe"),
    path("mess/cancel/", views.student_mess_cancel, name="student_mess_cancel"),
]
