from django.urls import path, include
from . import views
from . import views_extra  # Aggiungiamo l'import per views_extra

app_name = 'anagrafica'

# Pattern URL per l'app anagrafica
urlpatterns = [
    # Dashboard
    path('', views.dashboard_anagrafica, name='dashboard'),
    
    # ========== RAPPRESENTANTI ==========
    path('rappresentanti/', include([
        path('', views.RappresentanteListView.as_view(), name='elenco_rappresentanti'),
        path('nuovo/', views.RappresentanteCreateView.as_view(), name='nuovo_rappresentante'),
        path('<int:pk>/', views.RappresentanteDetailView.as_view(), name='dettaglio_rappresentante'),
        path('<int:pk>/modifica/', views.RappresentanteUpdateView.as_view(), name='modifica_rappresentante'),
        path('<int:pk>/elimina/', views.RappresentanteDeleteView.as_view(), name='elimina_rappresentante'),
    ])),
    
    # ========== CLIENTI ==========
    path('clienti/', include([
        path('', views.ClienteListView.as_view(), name='elenco_clienti'),
        path('nuovo/', views.ClienteCreateView.as_view(), name='nuovo_cliente'),
        path('<int:pk>/', views.ClienteDetailView.as_view(), name='dettaglio_cliente'),
        path('<int:pk>/modifica/', views.ClienteUpdateView.as_view(), name='modifica_cliente'),
        path('<int:pk>/elimina/', views.ClienteDeleteView.as_view(), name='elimina_cliente'),
    ])),
    
    # ========== FORNITORI ==========
    path('fornitori/', include([
        path('', views.FornitoreListView.as_view(), name='elenco_fornitori'),
        path('nuovo/', views.FornitoreCreateView.as_view(), name='nuovo_fornitore'),
        path('<int:pk>/', views.FornitoreDetailView.as_view(), name='dettaglio_fornitore'),
        path('<int:pk>/modifica/', views.FornitoreUpdateView.as_view(), name='modifica_fornitore'),
        path('<int:pk>/elimina/', views.FornitoreDeleteView.as_view(), name='elimina_fornitore'),
    ])),
    
    # ========== API E UTILITIES ==========
    # Ricerca AJAX
    path('api/search/', views.api_search_anagrafica, name='api_search'),
    
    # Export dati
    path('export/', views.export_anagrafica, name='export_anagrafica'),
    
    # Toggle attivo/inattivo
    path('toggle/<str:tipo>/<int:pk>/', views.toggle_attivo, name='toggle_attivo'),
    
    # ========== API AGGIUNTIVE ==========
    # URL per autocompletamento rappresentanti (da views_extra)
    path('api/rappresentanti/', views_extra.rappresentanti_api, name='rappresentanti_api'),
    
    # URL per statistiche dashboard (da views_extra)
    path('api/stats/', views_extra.dashboard_stats_api, name='dashboard_stats_api'),
    
    # URL per validazione campi (da views_extra)
    path('api/validate/partita-iva/', views_extra.validate_partita_iva, name='validate_partita_iva'),
    path('api/validate/codice-fiscale/', views_extra.validate_codice_fiscale, name='validate_codice_fiscale'),
    
    # URL legacy per retrocompatibilità (se necessario)
    path('vedirappresentante/<int:pk>/', views.RappresentanteDetailView.as_view(), name='vedirappresentante'),
    path('vedicliente/<int:pk>/', views.ClienteDetailView.as_view(), name='vedicliente'),
    path('vedifornitore/<int:pk>/', views.FornitoreDetailView.as_view(), name='vedifornitore'),
]

# Pattern extra per funzionalità avanzate
extra_patterns = [
    # Reports e stampe (da views_extra)
    path('reports/', include([
        path('rappresentanti-pdf/', views_extra.rappresentanti_report_pdf, name='rappresentanti_pdf'),
        path('clienti-pdf/', views_extra.clienti_report_pdf, name='clienti_pdf'),
        path('fornitori-pdf/', views_extra.fornitori_report_pdf, name='fornitori_pdf'),
    ])),
    
    # Import/Export avanzato (da views_extra)
    path('import/', include([
        path('clienti/', views_extra.ImportClientiView.as_view(), name='import_clienti'),
        path('fornitori/', views_extra.ImportFornitoriView.as_view(), name='import_fornitori'),
    ])),
    
    # Operazioni batch (da views_extra)
    path('batch/', include([
        path('attiva-multipli/', views_extra.attiva_multipli, name='attiva_multipli'),
        path('disattiva-multipli/', views_extra.disattiva_multipli, name='disattiva_multipli'),
        path('elimina-multipli/', views_extra.elimina_multipli, name='elimina_multipli'),
    ])),
]

# Aggiungi pattern extra
urlpatterns += extra_patterns