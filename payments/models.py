from django.db import models
from django.core.mail import send_mail
from django.conf import settings

from dynamic_widgets.models import DynamicModelBase

from entities.models import User, Raffle, Ticket

class Order(DynamicModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='orders')
    tickets_quantity = models.IntegerField()

    class STATUS_CHOICES(models.TextChoices):
        PENDING = 'pending'
        APPROVED = 'approved'
        REJECTED = 'rejected'

    status = models.CharField(max_length=255, choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.PENDING)
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.tickets_quantity * 1.5

    def approve(self):
        self.status = self.STATUS_CHOICES.APPROVED
        self.save()
        
        tickets = [
            Ticket(
                raffle=self.raffle,
                user=self.user,
                order=self
            )
            for _ in range(self.tickets_quantity)
        ]

        Ticket.objects.bulk_create(tickets)

        subject = f'Compra de tickets para la rifa: {self.raffle.name}'
        message = (
            f'Hola {self.user.first_name},\n\n'
            f'Gracias por tu compra de {self.tickets_quantity} ticket(s) para la rifa "{self.raffle.name}".\n\n'
            f'Mucha suerte y gracias por participar.\n\n'
            'Atentamente,\n'
            'El equipo de Rifas 24'
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [self.user.email])