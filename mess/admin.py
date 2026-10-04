from django.contrib import admin
from .models import MessSubscription

@admin.register(MessSubscription)
class MessSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription_id', 'student', 'plan', 'amount', 'start_date', 'end_date', 'status']
    list_filter = ['plan', 'status']
    search_fields = ['student__name', 'subscription_id']
