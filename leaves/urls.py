from django.urls import path
from . import views

urlpatterns = [
    path("leaves/", views.admin_leave_list, name="admin_leave_list"),
    path("leaves/<int:leave_id>/action/", views.admin_leave_action, name="admin_leave_action"),
]
