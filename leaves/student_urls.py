from django.urls import path
from . import views

urlpatterns = [
    path("leaves/", views.student_leave_list, name="student_leave_list"),
    path("leaves/apply/", views.student_leave_apply, name="student_leave_apply"),
    path("leaves/<int:leave_id>/cancel/", views.student_leave_cancel, name="student_leave_cancel"),
]
