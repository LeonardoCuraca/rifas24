import random

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail

from dynamic_widgets.models import DynamicModelBase # Asumiendo el origen de tu base

class User(AbstractUser, DynamicModelBase):
    email = models.EmailField('Correo electrónico', unique=True)
    
    phone = models.CharField('Número de teléfono (Yape)', max_length=15, unique=True)
    
    first_name = models.CharField('Nombres', max_length=150)
    last_name = models.CharField('Apellidos', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

    @property
    def masked_full_name(self):
        return (
            f"{self.first_name[:3]}{'*' * len(self.first_name[3:])} "
            f"{self.last_name[:3]}{'*' * len(self.last_name[3:])}"
        ).strip()
        
class Raffle(DynamicModelBase):
    name = models.CharField(max_length=255)
    description = models.TextField()

    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def select_winner(self):
        tickets = self.tickets.all()
        winner = random.choice(tickets)
        self.winner = winner.user
        self.save()
        
        subject = f'¡Felicidades! Has ganado la rifa: {self.name}'
        message = (
            f'Hola {self.winner.first_name},\n\n'
            f'¡Felicitaciones! Has sido seleccionado como ganador de la rifa "{self.name}". '
            f'{self.description}\n\n'
            'Nos pondremos en contacto pronto con más detalles.\n\n'
            '¡Gracias por participar!'
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [self.winner.email])

class Ticket(DynamicModelBase):
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    order = models.ForeignKey('payments.Order', on_delete=models.CASCADE, related_name='tickets')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)