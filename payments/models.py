from django.db import models
from entities.models import DynamicModelBase

from entities.models import User, Raffle

class Order(DynamicModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='orders')
    tickets_quantity = models.IntegerField()

    class Status(models.TextChoices):
        PENDING = 'pending'
        APPROVED = 'approved'
        REJECTED = 'rejected'

    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.tickets_quantity * 1.5