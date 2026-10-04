from django.urls import path
from . import views

urlpatterns = [
    path("complaints/", views.complaint_list, name="complaint_list"),
    path("complaints/<int:pk>/resolve/", views.complaint_resolve, name="complaint_resolve"),
]
