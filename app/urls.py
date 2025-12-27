from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.views.generic import RedirectView

panel_patterns = [
	path('', include('panel.urls')),
	path('entities/', include('entities.urls')),
]

urlpatterns = [
	path('', include('website.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),

	path('panel/', include(panel_patterns)),
	path('payments/', include('payments.urls')),

	path('chaining/', include('smart_selects.urls')),
	path('dynamic-widgets/', include('dynamic_widgets.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# serve static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)