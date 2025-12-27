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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)