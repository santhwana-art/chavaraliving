from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_add, name="student_add"),
    path("students/<int:pk>/edit/", views.student_edit, name="student_edit"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
]
