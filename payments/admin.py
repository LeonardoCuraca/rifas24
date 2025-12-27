from django.contrib import admin

from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'raffle__name', 'tickets_quantity', 'status', 'created_at']
    ordering = ['-created_at']