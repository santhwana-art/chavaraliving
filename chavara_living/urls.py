from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('admin-panel/', include('students.urls')),
    path('admin-panel/', include('rooms.urls')),
    path('admin-panel/', include('complaints.urls')),
    path('admin-panel/', include('fees.urls')),
    path('admin-panel/', include('mess.urls')),
    path('admin-panel/', include('leaves.urls')),
    path('student/', include('students.student_urls')),
    path('student/', include('rooms.student_urls')),
    path('student/', include('complaints.student_urls')),
    path('student/', include('fees.student_urls')),
    path('student/', include('mess.student_urls')),
    path('student/', include('leaves.student_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
