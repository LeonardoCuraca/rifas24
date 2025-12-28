from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'raffle__name', 'tickets_quantity', 'status', 'created_at', 'approve']
    ordering = ['-created_at']

    def approve(self, obj):
        if obj.payment_proof and obj.status != Order.STATUS_CHOICES.APPROVED:
            return format_html('<a href="{}">Aprovar</a>', f'approve-order/{obj.id}/')
        else:
            return '-'
    approve.short_description = 'Approve Order'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('approve-order/<uuid:order_id>/', self.admin_site.admin_view(self.approve_order), name='approve-order'),
        ]
        return my_urls + urls

    def approve_order(self, request, order_id):
        order = Order.objects.get(id=order_id)
        order.approve()
        messages.success(request, f'Order {order.id} has been approved and tickets assigned.')
        return redirect(reverse('admin:payments_order_changelist'))