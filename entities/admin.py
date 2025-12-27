from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from entities.models import User, Raffle, Ticket

admin.site.register(User)

@admin.register(Raffle)
class RaffleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'winner', 'pick_winner']
    search_fields = ['name']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    def pick_winner(self, obj):
        if obj.winner:
            return '-'
        else:
            return format_html('<a href="{}">Pick winner</a>', f'pick-winner/{obj.id}/')
    pick_winner.short_description = 'Pick winner'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('pick-winner/<uuid:raffle_id>/', self.admin_site.admin_view(self.select_winner), name='pick-winner'),
        ]
        return my_urls + urls

    def select_winner(self, request, raffle_id):
        raffle = Raffle.objects.get(id=raffle_id)
        raffle.select_winner()
        messages.success(request, 'Winner selected for raffle: {}'.format(raffle.name))
        return redirect(reverse('admin:entities_raffle_changelist'))

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'raffle__name', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']