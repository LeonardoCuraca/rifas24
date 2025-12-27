from django 				import template, forms
from django.conf 			import settings
from django.forms			import ModelForm
from django.forms.models 	import ModelChoiceField, ModelChoiceIteratorValue
register = template.Library()

@register.filter()
def dynamic_form(form, request):
	add_fields 				= form.add_fields 				if hasattr(form, 'add_fields') 				else []
	vertical_orientation 	= form.vertical_orientation 	if hasattr(form, 'vertical_orientation') 	else False
	textarea_rows 			= form.textarea_rows 			if hasattr(form, 'textarea_rows') 			else 4
	horizontal_checkboxes 	= form.horizontal_checkboxes 	if hasattr(form, 'horizontal_checkboxes') 	else False

	form_html = ''
	for field in form:
		widget 		= field.field.widget
		widget_name	= widget.__class__.__name__

		col1 = 12 if vertical_orientation else 2
		col2 = 12 if vertical_orientation else 10
		reverse = ''

		# Checkboxes
		if widget_name == 'CheckboxInput' and horizontal_checkboxes:
			col1, col2, reverse = 11, 1, 'reverse align-items-center'

		# Hidden fields
		form_html += f'<div class="mb-3 row { reverse }" id="container_{ field.auto_id }"'
		form_html += ' style="display: none;">' if field.field.disabled or widget_name == 'HiddenInput' else '>'
			
		# Label
		form_html += f'<label for="id_{ field.name }" class="col-sm-{ col1 } col-form-label">{ field.label }'
		form_html += '*' if field.field.required else ''
		form_html += '</label>'

		# Input
		form_html += f'<div class="col-sm-{ col2 }">'
		form_html += f'<div class="input-group">'

		value 	= field.value() or ''
		name 	= field.name

		# add prefix
		if form.prefix:
			name = f'{ form.prefix }-{ name }'

		attrs = f'id="{ field.auto_id }" name="{ name }"'

		for k, v in widget.attrs.items():
			attrs += f' { k }="{ v }"'

		# Textarea
		if widget_name == 'Textarea':
			form_html += f'<textarea class="form-control" rows="{ textarea_rows }" { attrs }>{ value }</textarea>'

		# Password
		elif field.name == 'password':
			form_html += f'<input type="password" class="form-control" { attrs } placeholder="{ field.label }">'
			
		# Select
		elif widget_name in ['Select', 'ChainedSelect']:
			extra = ''

			if field.name in add_fields:
				extra = f'data-field="{ field.name }"'
			
			# Chained
			if widget_name == 'ChainedSelect':
				url = f"/chaining/filter/{ widget.to_app_name }/{ widget.to_model_name }/{ widget.chained_field }/{ widget.foreign_key_app_name }/{ widget.foreign_key_model_name }/{ widget.foreign_key_field_name }"
				field_text = str(field)
				data_chainfield = field_text.split('data-chainfield="')[1].split('"')[0]

				extra += f'data-chainfield="{ data_chainfield }"  data-url="{ url }" data-value="{ value if value else "null" }" auto_choose="true" data-empty_label="--------"'

				form_html += f'<select class="form-control chained-fk chosen-select" { attrs } { extra }>'
			
			# Normal
			else:
				form_html += f'<select class="form-select chosen-select" { attrs } { extra } >'

			# Options
			for option in field.field.choices:
				if isinstance(option[0], ModelChoiceIteratorValue):
					instance = field.field.queryset.model.objects.get(pk=option[0].value)

				form_html += f'<option value="{ option[0] }" { "selected" if option[0] == value else "" }>{ option[1] }</option>'
			form_html += "</select>"

			# Add button
			if isinstance(field.field, ModelChoiceField) and field.name in add_fields:
				form_html += '<div class="input-group-append btn-select">'
				form_html += f'<a class="btn btn-primary update-select" data-toggle="modal" href="#modal_{ field.name }"><i class="fa fa-plus"></i></a>'
				form_html += "</div>"

		# Multiple select
		elif widget_name in [ 'CheckboxSelectMultiple', 'SelectMultiple', 'ChainedSelectMultiple' ]:
			extra = ''

			if field.name in add_fields:
				extra = f'data-field="{ field.name }"'

			# Chained
			if widget_name == 'ChainedSelectMultiple':
				# Debug: Print possible attributes for ChainedSelectMultiple widget
				print(f"Widget type: {type(widget)}")
				print(f"Widget attributes: {dir(widget)}")
				print(f"Widget dict: {widget.__dict__}")
				url = f"/chaining/filter/{ widget.to_app_name }/{ widget.to_model_name }/{ widget.chain_field }/{ widget.foreign_key_app_name }/{ widget.foreign_key_model_name }/{ widget.foreign_key_field_name }"
				field_text = str(field)
				data_chainfield = field_text.split('data-chainfield="')[1].split('"')[0]

				extra += f'data-chainfield="{ data_chainfield }"  data-url="{ url }" data-value="{ value if value else "null" }" auto_choose="true" data-empty_label="--------"'

				form_html += f'<select class="form-control chained-fk chosen-select" { attrs } { extra } multiple>'
			
			else:
				form_html += f'<select class="form-select chosen-multi-select" { attrs } { extra } multiple>'

			for option in field.field.choices:
				instance = field.field.queryset.model.objects.get(pk=option[0].value)

				form_html += f'<option value="{ option[0] }"'
				form_html += 'selected' if value and option[0] in value else ''
				form_html += f'>{ option[1] }</option>'
					
			form_html += "</select>"

			# Add button
			if isinstance(field.field, ModelChoiceField) and field.name in add_fields:
				form_html += '<div class="input-group-append btn-select">'
				form_html += f'<a class="btn btn-primary update-select" data-toggle="modal" href="#modal_{ field.name }"><i class="fa fa-plus"></i></a>'
				form_html += "</div>"

		# Date Picker
		elif widget_name in [ 'DateTimeInput', 'DateInput' ]:
			form_html += f'<div class="input-group date">'
			form_html += f'<input type="{ widget.input_type }" { attrs } class="form-control" placeholder="{ field.label }" value="{ value }" />'
			form_html += (
				'<span class="btn btn-primary"><i class="fa fa-calendar"></i></span>'
			)
			form_html += "</div>"

		# Color Picker
		elif widget_name == 'ColorWidget':
			form_html += f'<div class="input-group">'
			form_html += f'<input type="color" { attrs } class="form-control  demo1" placeholder="{ field.label }" value="{ value }" />'
			form_html += f'<label for="{ field.auto_id }" class="btn btn-primary"><i class="fa-solid fa-palette"></i></label>'
			form_html += "</div>"

		# File Input
		elif widget_name == 'ClearableFileInput':
			form_html += f'<div class="input-group custom-file">'
			form_html += f'<input type="file" { attrs } class="form-control custom-file-input" />'
			form_html += f'<label for="{ field.auto_id }" class="btn btn-primary"><i class="fa-solid fa-file-circle-plus"></i></label>'
			form_html += "</div>"
			if value:
				form_html += f'<small class="form-text text-muted">Archivo actual: <a href="{ settings.MEDIA_URL }{ value }" target="_blank">{ value }</a></small>'

		# Clock Picker
		elif widget_name == "TimeInput":
			form_html += '<div class="input-group clockpicker" data-autoclose="true">'
			form_html += f'<input type="{ widget.input_type }" { attrs } class="form-control" placeholder="{ field.label }" value="{ value }" />'
			form_html += f'<label for="{ field.auto_id }" class="btn btn-primary"><i class="fa fa-clock"></i></label>'
			form_html += "</div>"

		# Checkbox
		elif widget_name == 'CheckboxInput':
			form_html += '<div class="form-check">'
			form_html += f'<input class="form-check-input" type="{ widget.input_type }" { attrs } id="{ field.auto_id }" { "checked" if value else "" }>'
			form_html += '</div>'

		# CKEditor
		elif widget_name == 'CKEditorWidget':
			widget.attrs['id'] = field.auto_id
			form_html += widget.render(field.name, value)
		
		# Default
		else:
			form_html += f'<input type="{ widget.input_type }" { attrs } class="form-control" placeholder="{ field.label }" value="{ value }" />'
		
		form_html += '</div>'
		
		if field.help_text:
			form_html += '<span class="form-text m-b-none">'
			form_html += f"{ field.help_text }"
			form_html += '</span>'

		form_html += '</div>'

		form_html += '</div>'
	return form_html


@register.filter
def dynamic_modals(form, request):
	add_fields 	= form.add_fields 	if hasattr(form, 'add_fields') 	else []
	modal_size	= form.modal_size 	if hasattr(form, 'modal_size') 	else 'md'

	form_html = ''
	for field in form:
		if isinstance(field.field, ModelChoiceField) and field.name in add_fields:
			
			class Form(ModelForm):
				class Meta:
					model = field.field.queryset.model

			modal_form = Form()

			field_extra_field_model = f'{field.name}_extra_field_model'
			field_extra_field_value_model = f'{field.name}_extra_field_value_model'
			print(field_extra_field_model, field_extra_field_value_model)
			if hasattr(form, field_extra_field_model) and hasattr(form, field_extra_field_value_model):
				modal_form.extra_field_model = getattr(form, field_extra_field_model)
				modal_form.extra_field_value_model = getattr(form, field_extra_field_value_model)

			if hasattr(modal_form, 'extra_field_model'):
				extra_fields = modal_form.extra_field_model.objects.filter(company = request.user.company)
				for extra_field in extra_fields:
					params = { 'label': extra_field.name, 'required': False }
						
					if extra_field.type == modal_form.extra_field_model.Type.TEXTO:
						modal_form.fields[extra_field.slug] = forms.CharField(**params)
					elif extra_field.type == modal_form.extra_field_model.Type.NUMERO:
						modal_form.fields[extra_field.slug] = forms.IntegerField(**params)
					elif extra_field.type == modal_form.extra_field_model.Type.FECHA:
						modal_form.fields[extra_field.slug] = forms.DateField(**params)
					elif extra_field.type == modal_form.extra_field_model.Type.HORA:
						modal_form.fields[extra_field.slug] = forms.TimeField(**params)
					elif extra_field.type == modal_form.extra_field_model.Type.SELECCION:
						params['choices'] = [(option.value, option.name) for option in extra_field.options.all()]
						modal_form.fields[extra_field.slug] = forms.ChoiceField(**params)

			form_html += f'<div class="modal fade" id="modal_{ field.name }" aria-hidden="true">'
			form_html += f'<div class="modal-dialog modal-{ modal_size } modal-dialog-centered">'
			form_html += '<div class="modal-content">'
			form_html += '<div class="modal-body">'
			form_html += f'<h3 class="m-t-none m-b text-capitalize">{ field.field.queryset.model._meta.verbose_name }</h3>'

			form_html += f'<form id="form_{ field.name }" onsubmit="submitForm(this); return false;" method="post" action="/dynamic-widgets/{ field.field.queryset.model._meta.app_label }/{ field.field.queryset.model._meta.model_name }/create/" data-field="{ field.name }">'
			form_html += dynamic_form(modal_form, request)
			form_html += '<button type="submit" class="btn btn-primary">Guardar</button>'
			form_html += '</form>'

			form_html += '</div>'
			form_html += '</div>'
			form_html += '</div>'
			form_html += '</div>'
	return form_html
