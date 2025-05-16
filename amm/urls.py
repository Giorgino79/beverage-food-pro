# amm/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Vista per la root che reindirizza alla landing page
def home_redirect(request):
    """Reindirizza alla landing page se non loggato, alla dashboard se loggato"""
    if request.user.is_authenticated:
        return redirect('home:index')  # Dashboard per utenti loggati
    else:
        return redirect('home:landing_page')  # Landing page per utenti anonimi

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Root URL - reindirizza alla landing page o dashboard
    path('', home_redirect, name='home_redirect'),
    
    # App URLs
    path('home/', include('home.urls')),  # App home (dashboard, chat, ecc.)
    path('dipendenti/', include('dipendenti.urls')),  # App dipendenti (login, gestione utenti)
    
    # AllAuth URLs (se necessario)
    path('accounts/', include('allauth.urls')),
    
    # Django Select2
    path('select2/', include('django_select2.urls')),
    
    # Debug Toolbar (solo in debug mode)
    path('__debug__/', include('debug_toolbar.urls')),
    
    path('anagrafica/', include('anagrafica.urls')),
    path('automezzi/', include('automezzi.urls')),
    path('ordini/', include('ordini.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),   
]

# Servire i file media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)