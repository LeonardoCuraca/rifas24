from django.db import models
from django.urls import reverse
from uuid import uuid4

class DynamicModelBase(models.Model):
	model = None

	id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

	class Meta:
		abstract = True

	def get_list_url(self):
		return reverse(f'{ self._meta.app_label }:{ self._meta.model_name }-list')

	def get_detail_url(self):
		if hasattr(self, 'get_absolute_url'):
			return self.get_absolute_url()
		return reverse(f'{ self._meta.app_label }:{ self._meta.model_name }-detail', args=(self.id,))

	def get_edit_url(self):
		return reverse(f'{ self._meta.app_label }:{ self._meta.model_name }-update', args=(self.id,))

	def get_delete_url(self):
		return reverse('dynamic-widgets:model-delete', kwargs={'app_name': self._meta.app_label, 'model_name': self._meta.model_name, 'pk': self.pk})
	
	def get_hide_url(self):
		return reverse('dynamic-widgets:model-delete', kwargs={'app_name': self._meta.app_label, 'model_name': self._meta.model_name, 'pk': self.pk}) + '?logic_delete'
	
	def get_show_url(self):
		return reverse('dynamic-widgets:model-show', kwargs={'app_name': self._meta.app_label, 'model_name': self._meta.model_name, 'pk': self.pk})