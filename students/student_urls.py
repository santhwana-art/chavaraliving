from django.urls import path
from students import views

urlpatterns = [
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("profile/", views.student_profile, name="student_profile"),
]
