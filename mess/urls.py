from django.urls import path
from . import views

# Admin-side mess URLs — prefix: admin-panel/
urlpatterns = [
    path("mess/", views.admin_mess_dashboard, name="admin_mess_dashboard"),
]
