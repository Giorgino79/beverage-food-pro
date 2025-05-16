from django.urls import path
from . import views

app_name = 'dipendenti'

urlpatterns = [
    # Autenticazione
    path('', views.entra, name='login'),
    path('esci/', views.esci, name='esci'),
    
    # Gestione Dipendenti
    path('elenco/', views.DipendenteListView.as_view(), name='elencodipendenti'),
    path('nuovo/', views.DipendenteCreateView.as_view(), name='registradipendente'),
    path('vedi/<int:pk>/', views.DipendenteDetailView.as_view(), name='vedidipendente'),
    path('aggiorna/<int:pk>/', views.DipendenteUpdateView.as_view(), name='aggiornadipendente'),
    
    # Gestione Allegati
    path('allegato/nuovo/<int:dipendente_id>/', views.AllegatoCreateView.as_view(), name='nuovo_allegato'),
    path('allegato/elimina/<int:pk>/', views.AllegatoDeleteView.as_view(), name='elimina_allegato'),
    
    # Gestione Presenze
    path('giornata/nuova/', views.GiornataCreateView.as_view(), name='iniziogiornata'),
    path('giornata/aggiorna/<int:pk>/', views.GiornataUpdateView.as_view(), name='aggiornagiornata'),
    
    # Reportistica
    path('report/mensile/', views.ReportMensileView.as_view(), name='stampa_mese_dipendente'),
    
    # Profilo Utente
    path('profilo/<str:username>/', views.profilo, name='profilo'),
    
    path('esci/', views.esci, name='esci'),
]