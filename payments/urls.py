from django.urls import path
from payments.views import *

app_name = 'payments'

urlpatterns = [
    path('webhook/', webhook, name='webhook'),
    path('generate-payment-link/', generate_payment_link, name='generate-payment-link'),

    path('success/', success, name='success'),
    path('failure/', failure, name='failure'),
    path('pending/', pending, name='pending'),
]