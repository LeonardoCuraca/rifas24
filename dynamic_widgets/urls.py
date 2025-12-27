
from django.urls import path

from dynamic_widgets.views import *

app_name = 'dynamic-widgets'

urlpatterns = [
    path('<str:app_name>/<str:model_name>/create/', ajax_model_create_view, name='ajax-model-create'),
	path('<str:app_name>/<str:model_name>/delete/<uuid:pk>/', model_delete_view, name='model-delete'),
	path('<str:app_name>/<str:model_name>/show/<uuid:pk>/', model_show_view, name='model-show'),
]