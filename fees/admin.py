from django.contrib import admin  # type: ignore
from .models import FeeRecord

@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'student', 'fee_type', 'amount', 'due_date', 'pay_date', 'status')
    list_filter = ('fee_type', 'status', 'due_date')
    search_fields = ('payment_id', 'student__name', 'description')
    readonly_fields = ('payment_id', 'created_at')
