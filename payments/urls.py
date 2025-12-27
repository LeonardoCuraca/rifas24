from django.urls import path
from payments.views import *

app_name = 'payments'

urlpatterns = [
    path('webhook/', webhook, name='webhook'),
    path('generate-payment-link/', generate_payment_link, name='generate-payment-link'),

    path('success/', success, name='success'),
    path('failure/', failure, name='failure'),
    path('pending/', pending, name='pending'),

    path('generate-order/', generate_order, name='generate-order'),
    path('order/<uuid:order_id>/', order, name='order'),
    path('upload-proof/<uuid:order_id>/', upload_proof, name='upload-proof'),
]