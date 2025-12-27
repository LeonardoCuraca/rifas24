import datetime
import json

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.db import models
from django.db.models.query import QuerySet
from django.forms import modelform_factory
from django.http import HttpResponse, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic import TemplateView

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from urllib.parse import unquote

from dynamic_widgets.utils import django_admin_keyword_search

@csrf_exempt
def ajax_model_create_view(request, app_name, model_name):
	model 	= apps.get_model(app_name, model_name)
	form 	= modelform_factory(model)
	
	if request.method == 'POST':
		form = form(request.POST, request.FILES)
		
		if form.is_valid():
			form.save()
			return JsonResponse({'status': 'ok', 'id': form.instance.id, 'str': str(form.instance)})
		else:
			message = ''.join([f'{ field }: { error }\r' for field in form.errors for error in form.errors[field]])
			return JsonResponse({'status': 'error', 'errors': message})
	return JsonResponse({'status': 'error'})

class DynamicBaseView():
	title 		= ''
	model 		= None
	object 		= None
	buttons 	= []
	add_another = True

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['project_name'] = settings.PROJECT_NAME
		context['model'] = {
			'verbose_name': self.model._meta.verbose_name,
			'verbose_name_plural': self.model._meta.verbose_name_plural,
		}
		context['app'] = self.model._meta.app_config.verbose_name
		context['app_url'] = reverse(f'{ self.model._meta.app_label }:index')
		# context['model_list_url'] = reverse(f'{ self.model._meta.app_label }:{ self.model._meta.model_name }-list')

		context['buttons'] = []
		for button in self.buttons:
			url = button[1].split('?')

			params = ''
			if len(url) > 1:
				params_list = url[1].split('&')
				params = '?'
				for param in params_list:
					params += param
					params += '&' if param != params_list[-1] else ''
			
			url = url[0].split('+')

			if len(url) > 1:
				if url[1] == 'params':
					params += '?'
					for key, value in self.request.GET.items():
						params += f'{key}={value}'
						params += '&' if param != params_list[-1] else ''

			to = url[0]

			try:
				to = reverse(url[0])
			except:
				pass

			redirect_url = to + params
			context['buttons'].append({
				'text': button[0],
				'url': redirect_url,
			})
		return context

def model_delete_view(request, app_name, model_name, pk):
	model = apps.get_model(app_name, model_name)	
	object = model.objects.get(pk=pk)

	if 'logic_delete' in request.GET:
		object.is_active = False
		object.save()
		messages.success(request, f'{ model._meta.verbose_name } oculto correctamente.')
	else:
		object.delete()
		messages.success(request, f'{ model._meta.verbose_name } eliminado correctamente.')
	
	if 'next' in request.GET:
		return redirect(request.GET.get('next'))
	return redirect(reverse(f'{ app_name }:{ model_name }-list'))

def model_show_view(request, app_name, model_name, pk):
	model = apps.get_model(app_name, model_name)
	object = model.objects.get(pk=pk)

	object.is_active = True
	object.save()
	
	messages.success(request, f'{ model._meta.verbose_name } activado correctamente.')

	if 'next' in request.GET:
		return redirect(request.GET.get('next'))
	return redirect(reverse(f'{ app_name }:{ model_name }-list'))

class DynamicListView(DynamicBaseView, ListView):
	template_name = 'dynamic_widgets/list.html'
	logic_delete = False
	actions = []
	resource = None
	search_fields = []
	list_hide_all = []
	list_hide_phone = []

	def get_queryset(self):
		queryset = super().get_queryset()

		filters = dict(self.request.GET.items())
		filters.pop('page', None)

		if 'q' in filters:
			query = filters['q']

			if 'api' in self.search_fields:
				self.search_fields.remove('api')

			if len(self.search_fields) > 0:
				queryset = django_admin_keyword_search(queryset, query, self.search_fields)
			filters.pop('q')

		filters_to_remove = []
		for key, value in filters.items():
			if value == '':
				filters_to_remove.append(key)
				continue

			if '__gte' in key:
				filters[key] = datetime.datetime.strptime(value, '%m/%d/%Y').strftime('%Y-%m-%d')
			elif '__lte' in key:
				filters[key] = datetime.datetime.strptime(value, '%m/%d/%Y').strftime('%Y-%m-%d 23:59:59')

		for key in filters_to_remove:
			filters.pop(key)

		if isinstance(queryset, QuerySet):
			queryset = queryset.filter(**filters)
		else:
			new_queryset = queryset
			for key, value in filters.items():
				new_queryset = [item for item in new_queryset if str(getattr(item, key)) == str(value)]
			queryset = new_queryset
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		self.title = 'Listado de ' + self.model._meta.verbose_name_plural.title() if not self.title else self.title

		if 'create' in self.actions:
			context['model_create_url'] = reverse(f'{ self.model._meta.app_label }:{ self.model._meta.model_name }-create')
		return context

	def post(self, request, *args, **kwargs):
		action = request.POST.get('action')
		if action == 'export':
			dataset = self.resource().export(self.get_queryset())
			return HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')

		return super().post(request, *args, **kwargs)

class DynamicFormBaseView():
	template_name = 'dynamic_widgets/form.html'
	vertical_form = False
	horizontal_checkboxes = False
	textarea_rows = 4
	
	formset_class = None
	fk_field = ''
	
	extra_field_model = None
	extra_field_value_model = None
	
	form_add_fields = []
	
	modal_size = 'md'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'].add_fields = self.form_add_fields

		for field in self.form_add_fields:
			field_extra_field_model = f'{field}_extra_field_model'
			field_extra_field_value_model = f'{field}_extra_field_value_model'
			if hasattr(self, field_extra_field_model) and hasattr(self, field_extra_field_value_model):
				setattr(context['form'], field_extra_field_model, getattr(self, field_extra_field_model))
				setattr(context['form'], field_extra_field_value_model, getattr(self, field_extra_field_value_model))

		context['form'].textarea_rows = self.textarea_rows
		context['form'].horizontal_checkboxes = self.horizontal_checkboxes
		context['form'].modal_size = self.modal_size

		if self.formset_class:
			context['formset'] = self.formset_class(instance=self.object) if self.object else self.formset_class()
			context['formset_model'] = {
				'related_name': self.formset_class.model._meta.get_field(self.fk_field)._related_name,
				'verbose_name': self.formset_class.model._meta.verbose_name,
				'verbose_name_plural': self.formset_class.model._meta.verbose_name_plural
			}

		if self.extra_field_model:
			extra_fields = self.extra_field_model.objects.filter(company = self.request.user.company)
			for extra_field in extra_fields:
				params = { 'label': extra_field.name, 'required': False }
				if self.object:
					params['initial'] = self.extra_field_value_model.objects.get_or_create(field=extra_field, object=self.object)[0].value
					
				if extra_field.type == self.extra_field_model.Type.TEXTO:
					context['form'].fields[extra_field.slug] = forms.CharField(**params)
				elif extra_field.type == self.extra_field_model.Type.NUMERO:
					context['form'].fields[extra_field.slug] = forms.IntegerField(**params)
				elif extra_field.type == self.extra_field_model.Type.FECHA:
					context['form'].fields[extra_field.slug] = forms.DateField(**params)
				elif extra_field.type == self.extra_field_model.Type.HORA:
					context['form'].fields[extra_field.slug] = forms.TimeField(**params)
				elif extra_field.type == self.extra_field_model.Type.SELECCION:
					params['choices'] = [(option.value, option.name) for option in extra_field.options.all()]
					context['form'].fields[extra_field.slug] = forms.ChoiceField(**params)

		return context
	
	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		if self.vertical_form:
			form.vertical_orientation = True
		return form
	
	def form_valid(self, form, formset=None):
		response = super().form_valid(form)
		if self.extra_field_model:
			extra_fields = self.extra_field_model.objects.filter(company = self.request.user.company)
			for extra_field in extra_fields:
				self.extra_field_value_model.objects.update_or_create(
					object = self.object,
					field = extra_field,
					defaults = {
						'value': self.request.POST.get(extra_field.slug)
					}
				)
		return response
	
	def get_success_url(self):
		if '_addanother' in self.request.POST:
			query = '?' + '&'.join([f'{k}={v}' for k, v in self.request.GET.items()])
			return reverse(f'{ self.model._meta.app_label }:{ self.model._meta.model_name }-create') + query
		else:
			if 'next' in self.request.GET:
				return unquote(self.request.GET['next'])
			
			if self.success_url:
				return self.success_url
			
			urlencode_str	= self.request.GET.urlencode()
			urlencode_query = f'?{ urlencode_str }' if urlencode_str else ''
			return reverse(f'{ self.model._meta.app_label }:{ self.model._meta.model_name }-list') + urlencode_query
	
class DynamicCreateView(DynamicBaseView, DynamicFormBaseView, CreateView):

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		self.title = 'Crear ' + self.model._meta.verbose_name.title() if not self.title else self.title

		if 'formset' in context:
			if context['formset']:
				context['formset'].can_delete = False

		return context
	
	def get_initial(self):
		initial = super().get_initial()
		for k, v in self.request.GET.items():
			try:
				field = self.model._meta.get_field(k)
				if field.is_relation:
					initial[k] = field.related_model.objects.get(pk=v)
				elif field.many_to_many:
					initial[k] = field.related_model.objects.filter(pk__in=v.split(','))
				else:
					initial[k] = v
			except:
				pass
		return initial

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		formset = self.formset_class(request.POST, request.FILES) if self.formset_class else None
		if form.is_valid() and (not self.formset_class or formset.is_valid()):
			return self.form_valid(form, formset)
		else:
			return self.form_invalid(form, formset)

	def form_valid(self, form, formset=None):
		self.object = form.save()
		if formset:
			instance = formset.save(commit=False)
			for i in instance:
				setattr(i, self.fk_field, self.object)
				i.save()
		return super().form_valid(form)

	def form_invalid(self, form, formset=None):
		return self.render_to_response(self.get_context_data(form=form, formset=formset))
		
class DynamicCalendarView(DynamicListView, DynamicCreateView):
	template_name = 'dynamic_widgets/calendar.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		data = []
		for obj in self.get_queryset():
			title = ''
			start = getattr(obj, self.data_date).strftime('%Y-%m-%d') + ' ' + getattr(obj, self.data_hour).strftime('%H:%M')
			color = getattr(obj, self.data_color)() if callable(getattr(obj, self.data_color)) else getattr(obj, self.data_color)

			if not self.data_title:
				title = obj.__str__()
			else:
				for expression in self.data_title:
					attr_title = ''

					if hasattr(obj, expression):
						attr = getattr(obj, expression)
						attr_title = attr() if callable(attr) else attr
					elif '__' in expression:
						result = ''
						for idx, attr in enumerate(expression.split('__')):
							if idx >= 1 and not result:
								result = ''
								break
							result = getattr(obj if not result else result, attr)() if callable(getattr(obj if not result else result, attr)) else getattr(obj if not result else result, attr)
						attr_title = result
					else:
						attr_title = expression

					title += f'{ attr_title } '

			data.append({ 'id': obj.pk, 'title': title, 'start': start, 'color': color })

		context['data'] = json.dumps(data)
		
		return context

class DynamicUpdateView(DynamicBaseView, DynamicFormBaseView, UpdateView):

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		self.title = 'Editar ' + self.model._meta.verbose_name.title() if not self.title else self.title
		
		if 'formset' in context:
			if context['formset']:
				context['formset'].extra = 0
				context['formset'].can_delete = True

		return context
    
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()
		formset = self.formset_class(request.POST, request.FILES, instance=self.object) if self.formset_class else None
		if form.is_valid() and (not self.formset_class or formset.is_valid()):
			return self.form_valid(form, formset)
		else:
			return self.form_invalid(form, formset)
        
	def form_valid(self, form, formset=None):
		self.object = form.save()
          
		if formset:
			instance = formset.save(commit=False)
			for i in instance:
				setattr(i, self.fk_field, self.object)
				i.save()

			for i in formset.deleted_objects:
				i.delete()
		return super().form_valid(form)
    
	def form_invalid(self, form, formset=None):
		return self.render_to_response(self.get_context_data(form=form, formset=formset))

class DynamicDetailView(DynamicBaseView, DetailView):
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		self.title = self.object if not self.title else self.title
		self.template_name = f'{self.model._meta.app_label}/{self.model._meta.model_name}/detail.html' if not self.template_name else self.template_name
		return context

class APICreateView(CreateView):

	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = form_class(json.loads(request.body))
		if form.is_valid():
			object = form.save()
			return JsonResponse({'status': 'success', 'id': object.pk})
		else:
			errors = {}
			for k, v in form.errors.items():
				errors[k] = []
				for error in v:
					errors[k].append(error)
			return JsonResponse({'status': 'error', 'message': errors})
