from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from entities.forms import CustomUserCreationForm, UserProfileForm
from entities.models import User, Raffle

from payments.models import Order

def index(request):
    today = date.today()

    live_raffles = Raffle.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
    ).order_by('end_date')

    upcoming_raffles = Raffle.objects.filter(
        start_date__gt=today
    ).order_by('start_date')
    
    past_winners = Raffle.objects.filter(
        end_date__lt=today,
        winner__isnull=False
    ).order_by('-end_date')[:6]

    context = {
        'live_raffles': live_raffles,
        'upcoming_raffles': upcoming_raffles,
        'past_winners': past_winners,
    }
    
    return TemplateResponse(request, 'website/index.html', context)


def raffle_detail(request, raffle_id):
    raffle = get_object_or_404(Raffle, pk=raffle_id)

    participants = raffle.tickets.values(
        'user__id',
        'user__username',
        'user__first_name',
        'user__last_name'
    ).annotate(
        total_tickets=Count('id')
    ).order_by('-total_tickets')

    participants = [
        {
            'id': participant['user__id'],
            'username': participant['user__username'],
            'full_name': (
                f"{participant['user__first_name'][:3]}{'*' * len(participant['user__first_name'][3:])} "
                f"{participant['user__last_name'][:3]}{'*' * len(participant['user__last_name'][3:])}"
            ).strip() or participant['user__username'],
            'tickets_bought': participant['total_tickets']
        }
        for participant in participants
    ]

    context = {
        'raffle': raffle,
        'participants': participants,
    }

    return TemplateResponse(request, 'website/raffle/detail.html', context)

class RegisterView(SuccessMessageMixin, CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_message = "¡Tu cuenta ha sido creada! Ya puedes participar en las rifas."

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email

        response = super().form_valid(form)
        
        login(self.request, self.object)

        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('website:index')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'website/settings/profile.html'
    success_url = reverse_lazy('website:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.instance
        old_email = user.__class__.objects.get(pk=user.pk).email
        result = super().form_valid(form)
        if form.cleaned_data.get('email') and form.cleaned_data['email'] != old_email:
            user.username = form.cleaned_data['email']
            user.save(update_fields=['username'])
        messages.success(self.request, "¡Perfil actualizado correctamente!")
        return result

class MyPurchasesListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'website/settings/my_purchases.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        orders = Order.objects.filter(user=self.request.user).order_by('-created_at')
        return orders