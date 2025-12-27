from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse
from django.template.defaultfilters import capfirst, floatformat

register = template.Library()

@register.filter
def clear_filters(field, request):
    splited = field.split('-')
    filters = list(request.GET.items())
    link = '?'
    c = 1
    
    filters = [x for x in filters if x[0] != splited[0]]

    for filter in filters:
        if filter[0] == 'page':
            break
        if filter[0] != splited[0]:
            link += filter[0] + '=' + filter[1]
            if len(splited) == 2 and c == len(filters):
                break
            link += '&'
        c += 1
    return link

@register.filter
def dynamic_search(request):
	html = ''

	value = request.GET.get('q', '')

	html += '<div class="form-group">'
	html += f'<label class="col-form-label" for="q">Buscar</label>'
	html += '<div class="input-group">'
	html += f'<input type="text" id="q" name="q" class="form-control" value="{ value }" placeholder="Buscar...">'
	html += '<span class="input-group-append">'
	html += '<button type="submit" class="btn btn-primary"><i class="fa-solid fa-magnifying-glass"></i></button>'
	html += '</span>'
	html += '</div>'
	html += '</div>'

	for k, v in request.GET.items():
		if k != 'q' and k != 'page':
			print(k)
			html += f'<input type="hidden" name="{ k }" value="{ v }" />'
	
	return html

@register.filter
def dynamic_filters(view, request):
	list_filter = view.list_filter if hasattr(view, 'list_filter') else []
	filter_by_company = view.filter_by_company if hasattr(view, 'filter_by_company') else False
	filter_by_branch = view.filter_by_branch if hasattr(view, 'filter_by_branch') else False

	model = view.model

	html = ''

	for field in model._meta.get_fields():
		if field.name in list_filter:
			html += '<div class="col-sm-2">'
			html += '<div class="form-group">'
			html += f'<label class="col-form-label" for="{ field.name }">{ field.verbose_name }</label>'
			html += '<div class="dropdown">'
			
			value = request.GET.get(field.name, '')

			ul_html = ''

			ul_html += '<ul class="dropdown-menu mt-2" x-placement="bottom-start">'
			ul_html += '<li><a href="' + clear_filters(field.name, request) + '">Todos</a></li>'

			icon = ''
			label = 'Todos'
			if field.choices:
				for choice in field.choices:
					label = choice[1] if value == str(choice[0]) else label
					icon = '<i class="fa fa-check text-navy me-2"></i>' if str(choice[0]) == value else ''
					ul_html += f'<li><a href="{ clear_filters(field.name, request) }{ field.name }={ choice[0] }">{ icon }{ choice[1] }</a></li>'
			# if field is boolean
			elif field.get_internal_type() == 'BooleanField':
				options = [('True', 'Si'), ('False', 'No')]
				for option in options:
					label = option[1] if value == option[0] else label
					icon = '<i class="fa fa-check text-navy me-2"></i>' if option[0] == value else ''
					ul_html += f'<li><a href="{ clear_filters(field.name, request) }{ field.name }={ option[0] }">{ icon }{ option[1] }</a></li>'
			elif field.get_internal_type() == 'ForeignKey' or field.get_internal_type() == 'ManyToManyField':
				field_model = field.related_model
				queryset = field_model.objects.all()

				queryset = queryset.filter(company = request.user.company) if filter_by_company else queryset
				queryset = queryset.filter(branch = request.session.get('branch')) if filter_by_branch else queryset
				
				for item in queryset:
					label = item if value == str(item.id) else label
					icon = '<i class="fa fa-check text-navy me-2"></i>' if str(item.id) == value else ''
					ul_html += f'<li><a href="{ clear_filters(field.name, request) }{ field.name }={ item.id }">{ icon }{ item }</a></li>'

			ul_html += '</ul>'

			button_html = f'<button data-toggle="dropdown" class="btn btn-white dropdown-toggle w-100" type="button" aria-expanded="false">{ label }</button>'

			html += button_html + ul_html

			html += '</div>'
			html += '</div>'
			html += '</div>'

			list_filter = [x for x in list_filter if x != field.name]
		
	for filter in list_filter:
		field, fk = filter.split('__')
		queryset = view.get_queryset()
		# ex. queryset model is Schedule, it has a contact in it and I want to get a list o contact.company without double
		# relation is filter, contact is field.name
		from django.db.models import F

		queryset = queryset.annotate(**{ fk: F(filter) })

		fk_id_list = list(queryset.values_list(fk, flat=True).distinct())
		model = view.model._meta.get_field(field).related_model._meta.get_field(fk).related_model

		options = model.objects.filter(pk__in=fk_id_list)
		
		html += '<div class="col-sm-2">'
		html += '<div class="form-group">'
		html += f'<label class="col-form-label" for="{ filter }">{ model._meta.verbose_name }</label>'
		html += '<div class="dropdown">'

		value = request.GET.get(filter, '')

		ul_html = ''

		ul_html += '<ul class="dropdown-menu mt-2" x-placement="bottom-start">'
		ul_html += '<li><a href="' + clear_filters(filter, request) + '">Todos</a></li>'

		icon = ''
		label = 'Todos'
		for item in options:
			icon, label = ('<i class="fa fa-check text-navy me-2"></i>', item) if str(item.id) == value else ('', model._meta.verbose_name_plural)
			ul_html += f'<li><a href="{ clear_filters(filter, request) }{ filter }={ item.id }">{ icon }{ item }</a></li>'

		ul_html += '</ul>'

		button_html = f'<button data-toggle="dropdown" class="btn btn-white dropdown-toggle w-100" type="button" aria-expanded="false">{ label }</button>'

		html += button_html + ul_html

		html += '</div>'
		html += '</div>'
		html += '</div>'

	return html

@register.filter
def dynamic_table(view, request):
	object_list = view.get_context_data()['page_obj'] if 'page_obj' in view.get_context_data() else view.object_list
	list_display = view.list_display if hasattr(view, 'list_display') else []
	list_hide_all = view.list_hide_all if hasattr(view, 'list_hide_all') else []
	list_hide_phone = view.list_hide_phone if hasattr(view, 'list_hide_phone') else []
	
	actions = view.actions if hasattr(view, 'actions') else []

	html = ''

	html += '<table class="footable table table-stripped toggle-arrow-tiny">'

	html += '<thead>'
	html += '<tr>'
	for field in list_display:
		attrs = 'data-toggle="true"' if list_display.index(field) == 0 else ''
		attrs = 'data-hide="all"' if field in list_hide_all else attrs
		attrs = 'data-hide="phone"' if field in list_hide_phone else attrs

		try:
			model_field = view.model._meta.get_field(field)
			html += f'<th { attrs }>{ capfirst(model_field.verbose_name) }</th>'
		except:
			function = getattr(view, field)
			title = function.__name__ if hasattr(function, '__name__') else function.__class__.__name__
			if hasattr(function, 'short_description'):
				title = function.short_description
			html += f'<th { attrs }>{ title }</th>'

	if actions:
		html += '<th class="text-end">Acciones</th>'

	html += '</tr>'
	html += '</thead>'

	html += '<tbody>'
	for item in object_list:
		html += '<tr>'
		for field in list_display:
			from django.db.models import fields
			from django.urls import reverse
			try:
				if isinstance(item, dict):
					html += f'<td>{ item[field] }</td>'
				elif isinstance(view.model._meta.get_field(field), fields.IntegerField):
					html += f'<td>{ intcomma(floatformat(getattr(item, field), 0), False) }</td>'
				# datetime
				elif isinstance(view.model._meta.get_field(field), fields.DateTimeField):
					html += f'<td>{ getattr(item, field).strftime("%d/%m/%Y %H:%M:%S") }</td>'
				else:
					html += f'<td>{ getattr(item, field) }</td>'
			except:
				function = getattr(view, field)
				value = function(item)
				
				value = intcomma(floatformat(value, 0), False) if isinstance(value, float) else value
				value = intcomma(value, False)

				if hasattr(function, 'prefix'):
					value = f'{ function.prefix } { value }'

				if hasattr(function, 'suffix'):
					value = f'{ value } { function.suffix }'

				html += f'<td>{ value }</td>'
		
		if actions:
			html += '<td class="text-end">'

			urlencode_str	= request.GET.urlencode()
			urlencode_query = f'?{ urlencode_str }' if urlencode_str else ''

			banned_actions = ['view', 'edit', 'delete', 'hide', 'create', 'export']
			for action in actions:
				if action not in banned_actions:
					html += getattr(view, action)(item)

			if 'view' in actions:
				url = item.get_detail_url()
				html += f'<a href="{ url }" class="btn-white btn btn-xs"><i class="fa fa-eye"></i> Detalle</a>'
			if 'edit' in actions:
				url = item.get_edit_url()
				html += f'<a href="{ url }{ urlencode_query }" class="btn-white btn btn-xs"><i class="fa fa-edit"></i> Editar</a>'
			if 'delete' in actions:
				url = item.get_delete_url()
				html += f'<a href="{ url }{ urlencode_query }" class="btn-white btn btn-xs"><i class="fa fa-trash"></i> Eliminar</a>'
			if 'hide' in actions:
				url = item.get_delete_url()
				if not item.is_active:
					html += f'<a href="{ url }{ urlencode_query }" class="btn-white btn btn-xs"><i class="fa fa-trash"></i> Eliminar Permanentemente</a>'
					
					url = item.get_show_url()
					html += f'<a href="{ url }{ urlencode_query }" class="btn-white btn btn-xs"><i class="fa fa-eye"></i> Mostrar</a>'
				else:
					urlencode_query += '&logic_delete' if urlencode_query else '?logic_delete'
					html += f'<a href="{ url }{ urlencode_query }" class="btn-white btn btn-xs"><i class="fa fa-eye"></i> Ocultar</a>'

			html += '</td>'

		html += '</tr>'
	html += '</tbody>'

	if 'has_other_pages' in dir(object_list) and object_list.has_other_pages():
		html += '<tfoot>'
		html += '<tr>'
		html += f'<td colspan="{ len(list_display) + 1 }">'
		html += '<ul class="pagination pagination-sm float-end">'
		
		html += '<li class="page-item' + (' disabled' if not object_list.has_previous() else '') + '"><a class="page-link" href="' + ('' if not object_list.has_previous() else clear_filters('page', view.request) + 'page=1') + '">«</a></li>'
		html += '<li class="page-item' + (' disabled' if not object_list.has_previous() else '') + '"><a class="page-link" href="' + ('' if not object_list.has_previous() else clear_filters('page', view.request) + 'page=' + str(object_list.previous_page_number())) + '">‹</a></li>'
		
		for page_num in object_list.paginator.page_range:
			html += '<li class="page-item' + (' active' if object_list.number == page_num else '') + '">'
			html += '<a class="page-link" href="' + clear_filters('page', view.request) + 'page=' + str(page_num) + '">' + str(page_num) + '</a>'
			html += '</li>'
		
		html += '<li class="page-item' + (' disabled' if not object_list.has_next() else '') + '"><a class="page-link" href="' + ('' if not object_list.has_next() else clear_filters('page', view.request) + 'page=' + str(object_list.next_page_number())) + '">›</a></li>'
		html += '<li class="page-item' + (' disabled' if not object_list.has_next() else '') + '"><a class="page-link" href="' + ('' if not object_list.has_next() else clear_filters('page', view.request) + 'page=' + str(object_list.paginator.num_pages)) + '">»</a></li>'
		
		html += '</ul>'
		html += '</td>'
		html += '</tr>'
		html += '</tfoot>'

	html += '</table>'

	return html
