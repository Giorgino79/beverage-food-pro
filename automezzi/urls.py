# automezzi/urls.py

from django.urls import path, include
from . import views

app_name = 'automezzi'

urlpatterns = [
    # ===================== DASHBOARD E OVERVIEW =====================
    path('', views.dashboard_automezzi, name='dashboard'),
    path('scadenze/', views.scadenze_view, name='scadenze'),
    
    # ===================== TIPO CARBURANTE =====================
    path('tipi-carburante/', include([
        path('', views.TipoCarburanteListView.as_view(), name='tipi_carburante'),
        path('nuovo/', views.TipoCarburanteCreateView.as_view(), name='nuovo_tipo_carburante'),
        path('<int:pk>/modifica/', views.TipoCarburanteUpdateView.as_view(), name='modifica_tipo_carburante'),
        path('<int:pk>/elimina/', views.TipoCarburanteDeleteView.as_view(), name='elimina_tipo_carburante'),
    ])),
    
    # ===================== AUTOMEZZI =====================
    path('automezzi/', include([
        path('', views.AutomezzoListView.as_view(), name='lista'),
        path('nuovo/', views.AutomezzoCreateView.as_view(), name='nuovo'),
        path('<int:pk>/', views.AutomezzoDetailView.as_view(), name='dettaglio'),
        path('<int:pk>/modifica/', views.AutomezzoUpdateView.as_view(), name='modifica'),
        path('<int:pk>/elimina/', views.AutomezzoDeleteView.as_view(), name='elimina'),
        
        # ===================== DOCUMENTI AUTOMEZZO =====================
        path('<int:automezzo_pk>/documenti/', include([
            path('nuovo/', views.DocumentoCreateView.as_view(), name='nuovo_documento'),
            path('<int:pk>/modifica/', views.DocumentoUpdateView.as_view(), name='modifica_documento'),
            path('<int:pk>/elimina/', views.DocumentoDeleteView.as_view(), name='elimina_documento'),
        ])),
        
        # ===================== MANUTENZIONI AUTOMEZZO =====================
        path('<int:automezzo_pk>/manutenzioni/', include([
            path('nuovo/', views.ManutenzioneCreateView.as_view(), name='nuova_manutenzione'),
            path('<int:pk>/modifica/', views.ManutenzioneUpdateView.as_view(), name='modifica_manutenzione'),
            path('<int:pk>/completa/', views.manutenzione_completa, name='completa_manutenzione'),
        ])),
        
        # ===================== RIFORNIMENTI AUTOMEZZO =====================
        path('<int:automezzo_pk>/rifornimenti/', include([
            path('nuovo/', views.RifornimentoCreateView.as_view(), name='nuovo_rifornimento'),
            path('<int:pk>/modifica/', views.RifornimentoUpdateView.as_view(), name='modifica_rifornimento'),
        ])),
        
        # ===================== EVENTI AUTOMEZZO =====================
        path('<int:automezzo_pk>/eventi/', include([
            path('nuovo/', views.EventoCreateView.as_view(), name='nuovo_evento'),
            path('<int:pk>/modifica/', views.EventoUpdateView.as_view(), name='modifica_evento'),
            path('<int:pk>/risolvi/', views.evento_risolvi, name='risolvi_evento'),
        ])),
        
        # ===================== UTILITY AUTOMEZZO =====================
        path('<int:pk>/toggle-disponibilita/', views.toggle_disponibilita, name='toggle_disponibilita'),
        path('<int:pk>/aggiorna-statistiche/', views.aggiorna_statistiche, name='aggiorna_statistiche'),
        path('<int:pk>/report-consumi/', views.report_consumi, name='report_consumi'),
    ])),
    
    # ===================== LISTE GENERALI =====================
    path('manutenzioni/', views.ManutenzioniListView.as_view(), name='lista_manutenzioni'),
    path('eventi/', views.EventiListView.as_view(), name='lista_eventi'),
    
    # ===================== API E AJAX =====================
    path('api/', include([
        path('search/', views.api_automezzi_search, name='api_search'),
    ])),
    
    # ===================== EXPORT E BULK =====================
    path('export/', include([
        path('csv/', views.export_automezzi_csv, name='export_csv'),
    ])),
    path('bulk/', include([
        path('disponibilita/', views.bulk_aggiorna_disponibilita, name='bulk_disponibilita'),
    ])),
]