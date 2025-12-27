import json
import mercadopago

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from entities.models import Raffle, Ticket
from payments.models import Order

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

@csrf_exempt
def webhook(request):
    data = json.loads(request.body.decode('utf-8'))

    notification_type = data.get('type')
    resource_id = data.get('data', {}).get('id')
    
    if notification_type == 'payment':
        payment_response = sdk.payment().get(resource_id)
        payment = payment_response['response']

        external_reference = payment['external_reference']
        status = payment['status']

        order = Order.objects.get(id=external_reference)
        order.status = status
        order.save()
        
        tickets = [
            Ticket(
                raffle=order.raffle,
                user=order.user,
                order=order
            )
            for _ in range(order.tickets_quantity)
        ]

        Ticket.objects.bulk_create(tickets)

        subject = f'Compra de tickets para la rifa: {order.raffle.name}'
        message = (
            f'Hola {order.user.first_name},\n\n'
            f'Gracias por tu compra de {order.tickets_quantity} ticket(s) para la rifa "{order.raffle.name}".\n\n'
            f'Mucha suerte y gracias por participar.\n\n'
            'Atentamente,\n'
            'El equipo de Rifas 24'
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.user.email])

    return JsonResponse({'status': 'ok'})

@csrf_exempt
@login_required
def generate_payment_link(request):
    user = request.user
    
    raffle_id = request.POST.get('raffle_id')
    amount = int(request.POST.get('tickets_quantity', 1))

    raffle = Raffle.objects.get(id=raffle_id)
    if raffle.winner:
        return JsonResponse({
            'error': 'Esta rifa ya ha finalizado y tiene un ganador.',
            'should_reload': True
        }, status=400)
        

    order = Order.objects.create(
        user=user,
        raffle=raffle,
        tickets_quantity=amount,
    )

    preference_data = {
        'items': [
            {
                'title': f'{amount} Ticket{"" if amount == 1 else "s"} para la rifa {raffle.name}',
                'quantity': 1,
                'currency_id': 'PEN',
                'unit_price': amount * 1.50,
            }
        ],
        'back_urls': {
            'success': f'{settings.DOMAIN}/payments/success',
            'failure': f'{settings.DOMAIN}/payments/failure',
            'pending': f'{settings.DOMAIN}/payments/pending',
        },
        'external_reference': str(order.id),
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response['response']
    return JsonResponse(preference)

def success(request):
    external_reference = request.GET.get('external_reference')
    order = get_object_or_404(Order, id=external_reference)

    context = {
        'order': order,
        'payment_id': request.GET.get('payment_id'),
    }
    return TemplateResponse(request, 'payments/success.html', context)

def failure(request):
    external_reference = request.GET.get('external_reference')
    order = get_object_or_404(Order, id=external_reference)

    context = {
        'order': order,
        'payment_id': request.GET.get('payment_id'),
    }
    return TemplateResponse(request, 'payments/failure.html', context)

def pending(request):
    return TemplateResponse(request, 'payments/pending.html')