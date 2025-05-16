from django.urls import path
from . import views

app_name = 'ordini'  # Namespace per le URL dell'app

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    # URL per Prodotto
    path('categoria/nuova/', views.nuova_categoria, name='nuova_categoria'),  # Nuova URL per la creazione
    path('categorie/', views.lista_categorie, name='lista_categorie'),
    path('prodotti/', views.lista_prodotti, name='lista_prodotti'),
    path('prodotti/nuovo/', views.nuovo_prodotto, name='nuovo_prodotto'),
    path('prodotti/modifica/<int:pk>/', views.modifica_prodotto, name='modifica_prodotto'),
    path('prodotti/elimina/<int:pk>/', views.elimina_prodotto, name='elimina_prodotto'),

    # URL per Ordine
    path('', views.lista_ordini, name='lista_ordini'),  # URL principale per la lista degli ordini
    path('da-ricevere/', views.lista_ordini_da_ricevere, name='lista_ordini_da_ricevere'),
    path('ricevuti/', views.lista_ordini_ricevuti, name='lista_ordini_ricevuti'),
    path('nuovo/', views.nuovo_ordine, name='nuovo_ordine'),
    path('modifica/<int:pk>/', views.modifica_ordine, name='modifica_ordine'),
    path('conferma/<int:ordine_id>/', views.conferma_ordine, name='conferma_ordine'),
    path('ricevi/<int:ordine_id>/', views.ricevi_ordine, name='ricevi_ordine'),
    path('elimina/<int:pk>/', views.elimina_ordine, name='elimina_ordine'),

    # URL per Magazzino
    path('magazzino/', views.visualizza_magazzino, name='visualizza_magazzino'),
    

]