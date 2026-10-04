from django.contrib import admin  # type: ignore
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'contact', 'course', 'year', 'date_of_admission')
    search_fields = ('student_id', 'name', 'email', 'course')
    list_filter = ('year', 'course', 'date_of_admission')
    readonly_fields = ('student_id', 'created_at')
