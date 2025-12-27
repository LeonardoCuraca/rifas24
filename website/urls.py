from django.urls import path
from website.views import *

app_name = 'website'

urlpatterns = [
    path('', index, name='index'),
    path('raffles/<uuid:raffle_id>/', raffle_detail, name='raffle-detail'),

    path('register/', RegisterView.as_view(), name='register'),

    path('settings/profile/', ProfileUpdateView.as_view(), name='profile'),
    path('settings/my-purchases/', MyPurchasesListView.as_view(), name='my_purchases'),
]