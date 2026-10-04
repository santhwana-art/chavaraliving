from django.urls import path
from complaints import views

urlpatterns = [
    path("complaints/", views.student_complaint_list, name="student_complaint_list"),
    path("complaints/add/", views.student_complaint_add, name="student_complaint_add"),
]
