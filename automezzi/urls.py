from django.urls import path

from .views import (
    AutomezzoListView, AutomezzoDetailView, AutomezzoCreateView, AutomezzoUpdateView, AutomezzoDeleteView,
    ManutenzioneListView, ManutenzioneDetailView, ManutenzioneCreateView, ManutenzioneUpdateView, ManutenzioneDeleteView,
    RifornimentoListView, RifornimentoDetailView, RifornimentoCreateView, RifornimentoUpdateView, RifornimentoDeleteView,
    EventoAutomezzoListView, EventoAutomezzoDetailView, EventoAutomezzoCreateView, EventoAutomezzoUpdateView, EventoAutomezzoDeleteView, DashboardView
)

app_name = "automezzi"

urlpatterns = [
      path("", DashboardView.as_view(), name="dashboard"),
    # AUTOMEZZI
    path("automezzi/", AutomezzoListView.as_view(), name="automezzo_list"),
    path("automezzi/nuovo/", AutomezzoCreateView.as_view(), name="automezzo_create"),
    path("automezzi/<int:pk>/", AutomezzoDetailView.as_view(), name="automezzo_detail"),
    path("automezzi/<int:pk>/modifica/", AutomezzoUpdateView.as_view(), name="automezzo_update"),
    path("automezzi/<int:pk>/elimina/", AutomezzoDeleteView.as_view(), name="automezzo_delete"),

    # MANUTENZIONI
    path("manutenzioni/", ManutenzioneListView.as_view(), name="manutenzione_list"),
    path("manutenzioni/nuova/", ManutenzioneCreateView.as_view(), name="manutenzione_create"),
    path("manutenzioni/<int:pk>/", ManutenzioneDetailView.as_view(), name="manutenzione_detail"),
    path("manutenzioni/<int:pk>/modifica/", ManutenzioneUpdateView.as_view(), name="manutenzione_update"),
    path("manutenzioni/<int:pk>/elimina/", ManutenzioneDeleteView.as_view(), name="manutenzione_delete"),
    # annidate per automezzo
    path("automezzi/<int:automezzo_pk>/manutenzioni/", ManutenzioneListView.as_view(), name="manutenzione_list_automezzo"),
    path("automezzi/<int:automezzo_pk>/manutenzioni/nuova/", ManutenzioneCreateView.as_view(), name="manutenzione_create_automezzo"),

    # RIFORNIMENTI
    path("rifornimenti/", RifornimentoListView.as_view(), name="rifornimento_list"),
    path("rifornimenti/nuovo/", RifornimentoCreateView.as_view(), name="rifornimento_create"),
    path("rifornimenti/<int:pk>/", RifornimentoDetailView.as_view(), name="rifornimento_detail"),
    path("rifornimenti/<int:pk>/modifica/", RifornimentoUpdateView.as_view(), name="rifornimento_update"),
    path("rifornimenti/<int:pk>/elimina/", RifornimentoDeleteView.as_view(), name="rifornimento_delete"),
    # annidate per automezzo
    path("automezzi/<int:automezzo_pk>/rifornimenti/", RifornimentoListView.as_view(), name="rifornimento_list_automezzo"),
    path("automezzi/<int:automezzo_pk>/rifornimenti/nuovo/", RifornimentoCreateView.as_view(), name="rifornimento_create_automezzo"),

    # EVENTI
    path("eventi/", EventoAutomezzoListView.as_view(), name="evento_list"),
    path("eventi/nuovo/", EventoAutomezzoCreateView.as_view(), name="evento_create"),
    path("eventi/<int:pk>/", EventoAutomezzoDetailView.as_view(), name="evento_detail"),
    path("eventi/<int:pk>/modifica/", EventoAutomezzoUpdateView.as_view(), name="evento_update"),
    path("eventi/<int:pk>/elimina/", EventoAutomezzoDeleteView.as_view(), name="evento_delete"),
    # annidate per automezzo
    path("automezzi/<int:automezzo_pk>/eventi/", EventoAutomezzoListView.as_view(), name="evento_list_automezzo"),
    path("automezzi/<int:automezzo_pk>/eventi/nuovo/", EventoAutomezzoCreateView.as_view(), name="evento_create_automezzo"),
]