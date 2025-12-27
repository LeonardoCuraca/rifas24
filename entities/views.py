from django.template.response import TemplateResponse

from dynamic_widgets.views import DynamicListView, DynamicCreateView, DynamicUpdateView, DynamicDetailView

from entities.models import User, Raffle, Ticket

def index(request):
	return TemplateResponse(request, 'entities/index.html', {})

# ------------------ Users ------------------

class UserListView(DynamicListView):
	model 	= User
	paginate_by = 10
	
	search_fields 	= [ 'username', 'email' ]
	actions 		= [ 'create', 'edit', 'delete' ]
	
	list_display 	= [ 'username', 'email', 'first_name', 'last_name', 'date_joined' ]

class UserCreateView(DynamicCreateView):
    model 	= User
    fields	= [ 'username', 'password', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser' ]

    def form_valid(self, form, formset = None):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form, formset)

class UserUpdateView(DynamicUpdateView):
    model = User
    fields	= [ 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser' ]

# ------------------ Raffles ------------------

class RaffleListView(DynamicListView):
	model 		= Raffle
	paginate_by = 10
	
	search_fields 	= [ 'name' ]
	actions 		= [ 'create', 'edit', 'delete' ]
	
	list_display 	= [ 'name', 'base_amount', 'start_date', 'end_date', 'winner', 'created_at']
	
class RaffleCreateView(DynamicCreateView):
	model 	= Raffle
	fields	= [ 'name', 'base_amount', 'description', 'start_date', 'end_date' ]
	
class RaffleUpdateView(DynamicUpdateView):
	model = Raffle
	fields	= [ 'name', 'base_amount', 'description', 'start_date', 'end_date' ]

# ------------------ Tickets ------------------

class TicketListView(DynamicListView):
	model 	= Ticket
	paginate_by = 10
	
	search_fields 	= [ 'raffle__name', 'user__username' ]
	actions 		= [ 'create', 'edit', 'delete' ]
	
	list_display 	= [ 'raffle__name', 'user__username', 'created_at' ]
	