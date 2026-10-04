from django.urls import path
from . import views

urlpatterns = [
    path("fees/", views.fee_list, name="fee_list"),
    path("fees/add/", views.fee_add, name="fee_add"),
    path("fees/<int:pk>/edit/", views.fee_edit, name="fee_edit"),
    path("fees/<int:pk>/delete/", views.fee_delete, name="fee_delete"),
]
