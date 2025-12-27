from django.urls import path
from entities.views import *

app_name = 'entities'

urlpatterns = [
    path('', index, name='index'),

    # Users
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/update/<uuid:pk>/', UserUpdateView.as_view(), name='user-update'),

    # Raffles
    path('raffles/', RaffleListView.as_view(), name='raffle-list'),
    path('raffles/create/', RaffleCreateView.as_view(), name='raffle-create'),
    path('raffles/update/<uuid:pk>/', RaffleUpdateView.as_view(), name='raffle-update'),

    # Tickets
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
]