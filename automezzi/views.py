from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from .models import Automezzo, Manutenzione, Rifornimento, EventoAutomezzo
from .forms import (
    AutomezzoForm, ManutenzioneForm, RifornimentoForm, EventoAutomezzoForm
)
from django.utils import timezone
# AUTOMEZZI CRUD
class AutomezzoListView(LoginRequiredMixin, ListView):
    model = Automezzo
    template_name = "automezzi/automezzo_list.html"
    context_object_name = "automezzi"
    paginate_by = 20

class AutomezzoDetailView(LoginRequiredMixin, DetailView):
    model = Automezzo
    template_name = "automezzi/automezzo_detail.html"
    context_object_name = "automezzo"

class AutomezzoCreateView(LoginRequiredMixin, CreateView):
    model = Automezzo
    form_class = AutomezzoForm
    template_name = "automezzi/automezzo_form.html"
    success_url = reverse_lazy("automezzi:automezzo_list")

class AutomezzoUpdateView(LoginRequiredMixin, UpdateView):
    model = Automezzo
    form_class = AutomezzoForm
    template_name = "automezzi/automezzo_form.html"
    success_url = reverse_lazy("automezzi:automezzo_list")

class AutomezzoDeleteView(LoginRequiredMixin, DeleteView):
    model = Automezzo
    template_name = "automezzi/automezzo_confirm_delete.html"
    success_url = reverse_lazy("automezzi:automezzo_list")

# MANUTENZIONI CRUD
class ManutenzioneListView(LoginRequiredMixin, ListView):
    model = Manutenzione
    template_name = "automezzi/manutenzione_list.html"
    context_object_name = "manutenzioni"
    paginate_by = 20

    def get_queryset(self):
        # Se presente pk automezzo in url, filtra per automezzo
        pk = self.kwargs.get("automezzo_pk")
        qs = super().get_queryset()
        if pk:
            qs = qs.filter(automezzo_id=pk)
        return qs

class ManutenzioneDetailView(LoginRequiredMixin, DetailView):
    model = Manutenzione
    template_name = "automezzi/manutenzione_detail.html"
    context_object_name = "manutenzione"

class ManutenzioneCreateView(LoginRequiredMixin, CreateView):
    model = Manutenzione
    form_class = ManutenzioneForm
    template_name = "automezzi/manutenzione_form.html"

    def get_initial(self):
        initial = super().get_initial()
        # Se la manutenzione è creata da dettaglio automezzo
        pk = self.kwargs.get("automezzo_pk")
        if pk:
            initial["automezzo"] = pk
        return initial

    def get_success_url(self):
        return reverse_lazy("automezzi:manutenzione_list")

class ManutenzioneUpdateView(LoginRequiredMixin, UpdateView):
    model = Manutenzione
    form_class = ManutenzioneForm
    template_name = "automezzi/manutenzione_form.html"

    def get_success_url(self):
        return reverse_lazy("automezzi:manutenzione_list")

class ManutenzioneDeleteView(LoginRequiredMixin, DeleteView):
    model = Manutenzione
    template_name = "automezzi/manutenzione_confirm_delete.html"
    def get_success_url(self):
        return reverse_lazy("automezzi:manutenzione_list")

# RIFORNIMENTI CRUD
class RifornimentoListView(LoginRequiredMixin, ListView):
    model = Rifornimento
    template_name = "automezzi/rifornimento_list.html"
    context_object_name = "rifornimenti"
    paginate_by = 20

    def get_queryset(self):
        pk = self.kwargs.get("automezzo_pk")
        qs = super().get_queryset()
        if pk:
            qs = qs.filter(automezzo_id=pk)
        return qs

class RifornimentoDetailView(LoginRequiredMixin, DetailView):
    model = Rifornimento
    template_name = "automezzi/rifornimento_detail.html"
    context_object_name = "rifornimento"

class RifornimentoCreateView(LoginRequiredMixin, CreateView):
    model = Rifornimento
    form_class = RifornimentoForm
    template_name = "automezzi/rifornimento_form.html"

    def get_initial(self):
        initial = super().get_initial()
        pk = self.kwargs.get("automezzo_pk")
        if pk:
            initial["automezzo"] = pk
        return initial

    def get_success_url(self):
        return reverse_lazy("automezzi:rifornimento_list")

class RifornimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Rifornimento
    form_class = RifornimentoForm
    template_name = "automezzi/rifornimento_form.html"
    def get_success_url(self):
        return reverse_lazy("automezzi:rifornimento_list")

class RifornimentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Rifornimento
    template_name = "automezzi/rifornimento_confirm_delete.html"
    def get_success_url(self):
        return reverse_lazy("automezzi:rifornimento_list")

# EVENTI AUTOMEZZO CRUD
class EventoAutomezzoListView(LoginRequiredMixin, ListView):
    model = EventoAutomezzo
    template_name = "automezzi/evento_list.html"
    context_object_name = "eventi"
    paginate_by = 20

    def get_queryset(self):
        pk = self.kwargs.get("automezzo_pk")
        qs = super().get_queryset()
        if pk:
            qs = qs.filter(automezzo_id=pk)
        return qs

class EventoAutomezzoDetailView(LoginRequiredMixin, DetailView):
    model = EventoAutomezzo
    template_name = "automezzi/evento_detail.html"
    context_object_name = "evento"

class EventoAutomezzoCreateView(LoginRequiredMixin, CreateView):
    model = EventoAutomezzo
    form_class = EventoAutomezzoForm
    template_name = "automezzi/evento_form.html"

    def get_initial(self):
        initial = super().get_initial()
        pk = self.kwargs.get("automezzo_pk")
        if pk:
            initial["automezzo"] = pk
        return initial

    def get_success_url(self):
        return reverse_lazy("automezzi:evento_list")

class EventoAutomezzoUpdateView(LoginRequiredMixin, UpdateView):
    model = EventoAutomezzo
    form_class = EventoAutomezzoForm
    template_name = "automezzi/evento_form.html"
    def get_success_url(self):
        return reverse_lazy("automezzi:evento_list")

class EventoAutomezzoDeleteView(LoginRequiredMixin, DeleteView):
    model = EventoAutomezzo
    template_name = "automezzi/evento_confirm_delete.html"
    def get_success_url(self):
        return reverse_lazy("automezzi:evento_list")
    

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "automezzi/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["automezzi_count"] = Automezzo.objects.count()
        context["attivi_count"] = Automezzo.objects.filter(attivo=True).count()
        context["disponibili_count"] = Automezzo.objects.filter(disponibile=True, attivo=True, bloccata=False).count()
        context["automezzi_bloccati"] = Automezzo.objects.filter(bloccata=True)
        context["manutenzioni_in_corso"] = Manutenzione.objects.filter(completata=False)
        context["prossime_revisioni"] = Automezzo.objects.filter(data_revisione__gte=today).order_by('data_revisione')[:5]
        context["eventi_recenti"] = EventoAutomezzo.objects.order_by('-data_evento')[:5]
        context["rifornimenti_recenti"] = Rifornimento.objects.order_by('-data')[:5]
        return context