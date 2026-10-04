from django.urls import path
from fees import views

urlpatterns = [
    path("fees/", views.student_fee_list, name="student_fee_list"),
]
