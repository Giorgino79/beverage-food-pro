# automezzi/admin.py
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from .models import (
    TipoCarburante,
    Automezzo,
    DocumentoAutomezzo,
    Manutenzione,
    RifornimentoCarburante,
    EventoAutomezzo,
    StatisticheAutomezzo
)


# Filtri personalizzati
class ScadenzaDocumentoFilter(SimpleListFilter):
    """Filtro per documenti in scadenza"""
    title = 'Stato Scadenza'
    parameter_name = 'scadenza'

    def lookups(self, request, model_admin):
        return [
            ('scaduti', 'Scaduti'),
            ('15_giorni', 'Scadenza entro 15 giorni'),
            ('30_giorni', 'Scadenza entro 30 giorni'),
            ('90_giorni', 'Scadenza entro 90 giorni'),
        ]

    def queryset(self, request, queryset):
        from datetime import date, timedelta
        
        if self.value() == 'scaduti':
            return queryset.filter(data_scadenza__lt=date.today())
        elif self.value() == '15_giorni':
            return queryset.filter(
                data_scadenza__gte=date.today(),
                data_scadenza__lte=date.today() + timedelta(days=15)
            )
        elif self.value() == '30_giorni':
            return queryset.filter(
                data_scadenza__gte=date.today(),
                data_scadenza__lte=date.today() + timedelta(days=30)
            )
        elif self.value() == '90_giorni':
            return queryset.filter(
                data_scadenza__gte=date.today(),
                data_scadenza__lte=date.today() + timedelta(days=90)
            )


class ConsumoCarburaanteFilter(SimpleListFilter):
    """Filtro per consumi carburante"""
    title = 'Consumo per 100km'
    parameter_name = 'consumo'

    def lookups(self, request, model_admin):
        return [
            ('basso', 'Basso (< 6 L/100km)'),
            ('medio', 'Medio (6-10 L/100km)'),
            ('alto', 'Alto (> 10 L/100km)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'basso':
            return queryset.filter(statistiche__consumo_medio__lt=6)
        elif self.value() == 'medio':
            return queryset.filter(
                statistiche__consumo_medio__gte=6,
                statistiche__consumo_medio__lte=10
            )
        elif self.value() == 'alto':
            return queryset.filter(statistiche__consumo_medio__gt=10)


class StatoManutenzioneFilter(SimpleListFilter):
    """Filtro per stato manutenzioni"""
    title = 'Stato'
    parameter_name = 'stato'

    def lookups(self, request, model_admin):
        from datetime import date
        return [
            ('completate', 'Completate'),
            ('in_corso', 'In Corso'),
            ('in_ritardo', 'In Ritardo'),
            ('future', 'Programmate'),
        ]

    def queryset(self, request, queryset):
        from datetime import date
        
        if self.value() == 'completate':
            return queryset.filter(completata=True)
        elif self.value() == 'in_corso':
            return queryset.filter(
                completata=False,
                data_prevista__gte=date.today()
            )
        elif self.value() == 'in_ritardo':
            return queryset.filter(
                completata=False,
                data_prevista__lt=date.today()
            )
        elif self.value() == 'future':
            return queryset.filter(
                completata=False,
                data_prevista__gt=date.today()
            )


# Inline Models
class DocumentoAutomezzoInline(admin.TabularInline):
    """Inline per documenti automezzo"""
    model = DocumentoAutomezzo
    extra = 0
    fields = ['tipo', 'numero_documento', 'data_rilascio', 'data_scadenza', 'costo']
    readonly_fields = ['get_giorni_scadenza']
    
    def get_giorni_scadenza(self, obj):
        if obj and obj.data_scadenza:
            from datetime import date
            giorni = (obj.data_scadenza - date.today()).days
            if giorni < 0:
                return format_html('<span style="color: red;">Scaduto da {} giorni</span>', abs(giorni))
            elif giorni <= 15:
                return format_html('<span style="color: orange;">Scade tra {} giorni</span>', giorni)
            else:
                return format_html('<span style="color: green;">Scade tra {} giorni</span>', giorni)
        return '-'
    get_giorni_scadenza.short_description = 'Stato Scadenza'


class ManutenzioneInline(admin.StackedInline):
    """Inline per manutenzioni"""
    model = Manutenzione
    extra = 0
    fields = [
        ('tipo', 'completata'),
        'descrizione',
        ('data_prevista', 'data_effettuata'),
        ('costo_previsto', 'costo_effettivo'),
        'responsabile'
    ]
    readonly_fields = ['get_stato_display']

    def get_stato_display(self, obj):
        if obj and obj.data_prevista:
            from datetime import date
            if obj.completata:
                return format_html('<span style="color: green;">✓ Completata</span>')
            elif obj.data_prevista < date.today():
                return format_html('<span style="color: red;">⚠ In Ritardo</span>')
            else:
                return format_html('<span style="color: blue;">📅 Programmata</span>')
        return '-'
    get_stato_display.short_description = 'Stato'


class RifornimentoCarburanteInline(admin.TabularInline):
    """Inline per rifornimenti"""
    model = RifornimentoCarburante
    extra = 0
    fields = ['data_rifornimento', 'chilometri', 'litri', 'costo_totale', 'costo_per_litro']
    readonly_fields = ['costo_per_litro', 'get_consumo_calcolato']
    ordering = ['-data_rifornimento']

    def get_consumo_calcolato(self, obj):
        if obj and hasattr(obj, 'consumo_per_100km'):
            return f"{obj.consumo_per_100km:.2f} L/100km"
        return '-'
    get_consumo_calcolato.short_description = 'Consumo'


class EventoAutomezzoInline(admin.StackedInline):
    """Inline per eventi"""
    model = EventoAutomezzo
    extra = 0
    fields = [
        ('tipo', 'risolto'),
        'data_evento',
        'descrizione',
        ('costo', 'dipendente_coinvolto'),
        'file_allegato'
    ]


# Admin Classes
@admin.register(TipoCarburante)
class TipoCarburanteAdmin(admin.ModelAdmin):
    """Admin per tipi di carburante"""
    list_display = ['nome', 'costo_per_litro', 'get_automezzi_count']
    list_editable = ['costo_per_litro']
    search_fields = ['nome']
    ordering = ['nome']

    def get_automezzi_count(self, obj):
        count = obj.automezzo_set.count()
        return format_html(
            '<a href="{}?tipo_carburante__id__exact={}">{} automezzi</a>',
            reverse('admin:automezzi_automezzo_changelist'),
            obj.pk,
            count
        )
    get_automezzi_count.short_description = 'Automezzi'
    get_automezzi_count.admin_order_field = 'automezzo_count'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            automezzo_count=Count('automezzo')
        )


@admin.register(Automezzo)
class AutomezzoAdmin(admin.ModelAdmin):
    """Admin per automezzi"""
    list_display = [
        'targa', 'marca', 'modello', 'anno_immatricolazione',
        'get_assegnato_display', 'get_stato_display', 'chilometri_attuali',
        'get_consumo_medio', 'get_prossima_scadenza'
    ]
    list_filter = [
        'attivo', 'disponibile', 'tipo_carburante',
        'anno_immatricolazione', ConsumoCarburaanteFilter
    ]
    search_fields = ['targa', 'marca', 'modello', 'numero_telaio']
    list_editable = ['disponibile', 'chilometri_attuali']
    readonly_fields = [
        'get_eta_veicolo', 'get_km_percorsi', 'get_costo_totale',
        'get_consumo_medio', 'get_costo_per_km'
    ]
    fieldsets = [
        ('Identificazione', {
            'fields': ['targa', 'marca', 'modello', 'anno_immatricolazione']
        }),
        ('Dati Tecnici', {
            'fields': ['tipo_carburante', 'numero_telaio', 'cilindrata', 'potenza']
        }),
        ('Chilometraggio', {
            'fields': ['chilometri_iniziali', 'chilometri_attuali', 'get_km_percorsi']
        }),
        ('Dati Economici', {
            'fields': [
                'data_acquisto', 'prezzo_acquisto', 'data_vendita', 'prezzo_vendita',
                'get_costo_totale', 'get_costo_per_km'
            ],
            'classes': ['collapse']
        }),
        ('Assegnazione e Stato', {
            'fields': ['assegnato_a', 'attivo', 'disponibile']
        }),
        ('Statistiche', {
            'fields': ['get_eta_veicolo', 'get_consumo_medio'],
            'classes': ['collapse']
        })
    ]
    inlines = [DocumentoAutomezzoInline, ManutenzioneInline, RifornimentoCarburanteInline, EventoAutomezzoInline]
    
    # Actions
    actions = ['rendi_disponibili', 'rendi_non_disponibili', 'aggiorna_statistiche']

    def get_assegnato_display(self, obj):
        if obj.assegnato_a:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:dipendenti_dipendente_change', args=[obj.assegnato_a.pk]),
                obj.assegnato_a.get_full_name() or obj.assegnato_a.username
            )
        return '-'
    get_assegnato_display.short_description = 'Assegnato a'

    def get_stato_display(self, obj):
        html = ''
        if obj.attivo:
            html += '<span style="color: green;">● Attivo</span><br>'
        else:
            html += '<span style="color: red;">● Inattivo</span><br>'
        
        if obj.disponibile:
            html += '<span style="color: blue;">📍 Disponibile</span>'
        else:
            html += '<span style="color: orange;">📍 Assegnato</span>'
        return format_html(html)
    get_stato_display.short_description = 'Stato'

    def get_consumo_medio(self, obj):
        if hasattr(obj, 'statistiche') and obj.statistiche.consumo_medio:
            consumo = obj.statistiche.consumo_medio
            if consumo < 6:
                color = 'green'
            elif consumo <= 10:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {};">{:.2f} L/100km</span>',
                color, consumo
            )
        return '-'
    get_consumo_medio.short_description = 'Consumo Medio'

    def get_prossima_scadenza(self, obj):
        from datetime import date, timedelta
        prossima = obj.documenti.filter(
            data_scadenza__gte=date.today()
        ).order_by('data_scadenza').first()
        
        if prossima:
            giorni = (prossima.data_scadenza - date.today()).days
            if giorni <= 15:
                color = 'red'
            elif giorni <= 30:
                color = 'orange'
            else:
                color = 'green'
            return format_html(
                '<span style="color: {};">{} ({}gg)</span>',
                color, prossima.get_tipo_display(), giorni
            )
        return '-'
    get_prossima_scadenza.short_description = 'Prossima Scadenza'

    # Metodi readonly
    def get_eta_veicolo(self, obj):
        from datetime import date
        if obj.anno_immatricolazione:
            eta = date.today().year - obj.anno_immatricolazione
            return f"{eta} anni"
        return '-'
    get_eta_veicolo.short_description = 'Età Veicolo'

    def get_km_percorsi(self, obj):
        return obj.chilometri_attuali - obj.chilometri_iniziali
    get_km_percorsi.short_description = 'Km Percorsi'

    def get_costo_totale(self, obj):
        # Calcola costo totale considerando manutenzioni e carburante
        costo_manutenzioni = obj.manutenzioni.filter(
            completata=True,
            costo_effettivo__isnull=False
        ).aggregate(totale=Sum('costo_effettivo'))['totale'] or 0
        
        costo_carburante = obj.rifornimenti.aggregate(
            totale=Sum('costo_totale')
        )['totale'] or 0
        
        costo_totale = costo_manutenzioni + costo_carburante
        return f"€ {costo_totale:,.2f}"
    get_costo_totale.short_description = 'Costo Totale Gestione'

    def get_costo_per_km(self, obj):
        km_percorsi = obj.chilometri_attuali - obj.chilometri_iniziali
        if km_percorsi > 0 and hasattr(obj, 'statistiche'):
            return f"€ {obj.statistiche.costo_km_carburante:.3f}/km"
        return '-'
    get_costo_per_km.short_description = 'Costo per Km'

    # Actions
    def rendi_disponibili(self, request, queryset):
        count = queryset.update(disponibile=True)
        self.message_user(request, f"{count} automezzi resi disponibili.")
    rendi_disponibili.short_description = "Rendi disponibili"

    def rendi_non_disponibili(self, request, queryset):
        count = queryset.update(disponibile=False)
        self.message_user(request, f"{count} automezzi resi non disponibili.")
    rendi_non_disponibili.short_description = "Rendi non disponibili"

    def aggiorna_statistiche(self, request, queryset):
        count = 0
        for automezzo in queryset:
            # Trigger ricalcolo statistiche
            if hasattr(automezzo, 'statistiche'):
                automezzo.statistiche.save()
                count += 1
        self.message_user(request, f"Statistiche aggiornate per {count} automezzi.")
    aggiorna_statistiche.short_description = "Aggiorna statistiche"


@admin.register(DocumentoAutomezzo)
class DocumentoAutomezzoAdmin(admin.ModelAdmin):
    """Admin per documenti automezzi"""
    list_display = [
        'automezzo', 'tipo', 'numero_documento',
        'data_rilascio', 'data_scadenza', 'get_giorni_scadenza',
        'costo'
    ]
    list_filter = ['tipo', ScadenzaDocumentoFilter, 'data_rilascio']
    search_fields = [
        'automezzo__targa', 'numero_documento', 'automezzo__marca', 'automezzo__modello'
    ]
    date_hierarchy = 'data_scadenza'
    list_select_related = ['automezzo']
    
    def get_giorni_scadenza(self, obj):
        from datetime import date
        if obj.data_scadenza:
            giorni = (obj.data_scadenza - date.today()).days
            if giorni < 0:
                return format_html('<span style="color: red; font-weight: bold;">Scaduto da {} giorni</span>', abs(giorni))
            elif giorni <= 15:
                return format_html('<span style="color: red;">Scade tra {} giorni</span>', giorni)
            elif giorni <= 30:
                return format_html('<span style="color: orange;">Scade tra {} giorni</span>', giorni)
            else:
                return format_html('<span style="color: green;">Scade tra {} giorni</span>', giorni)
        return '-'
    get_giorni_scadenza.short_description = 'Stato Scadenza'
    get_giorni_scadenza.admin_order_field = 'data_scadenza'


@admin.register(Manutenzione)
class ManutenzioneAdmin(admin.ModelAdmin):
    """Admin per manutenzioni"""
    list_display = [
        'automezzo', 'tipo', 'data_prevista', 'data_effettuata',
        'get_stato_display', 'costo_previsto', 'costo_effettivo',
        'responsabile'
    ]
    list_filter = [
        'tipo', StatoManutenzioneFilter, 'completata',
        'data_prevista', 'responsabile'
    ]
    search_fields = [
        'automezzo__targa', 'descrizione', 'responsabile__first_name',
        'responsabile__last_name'
    ]
    date_hierarchy = 'data_prevista'
    list_select_related = ['automezzo', 'responsabile']
    
    fieldsets = [
        ('Identificazione', {
            'fields': ['automezzo', 'tipo', 'descrizione']
        }),
        ('Pianificazione', {
            'fields': ['data_prevista', 'costo_previsto', 'responsabile']
        }),
        ('Completamento', {
            'fields': ['completata', 'data_effettuata', 'costo_effettivo'],
            'classes': ['collapse']
        })
    ]

    def get_stato_display(self, obj):
        from datetime import date
        if obj.completata:
            return format_html('<span style="color: green; font-weight: bold;">✓ Completata</span>')
        elif obj.data_prevista < date.today():
            giorni = (date.today() - obj.data_prevista).days
            return format_html('<span style="color: red; font-weight: bold;">⚠ In ritardo di {} giorni</span>', giorni)
        else:
            giorni = (obj.data_prevista - date.today()).days
            return format_html('<span style="color: blue;">📅 Programmata (tra {} giorni)</span>', giorni)
    get_stato_display.short_description = 'Stato'


@admin.register(RifornimentoCarburante)
class RifornimentoCarburanteAdmin(admin.ModelAdmin):
    """Admin per rifornimenti carburante"""
    list_display = [
        'automezzo', 'data_rifornimento', 'chilometri',
        'litri', 'costo_totale', 'costo_per_litro',
        'get_consumo_display', 'effettuato_da'
    ]
    list_filter = [
        'data_rifornimento', 'automezzo__tipo_carburante', 'effettuato_da'
    ]
    search_fields = [
        'automezzo__targa', 'effettuato_da__first_name', 'effettuato_da__last_name'
    ]
    date_hierarchy = 'data_rifornimento'
    list_select_related = ['automezzo', 'effettuato_da']
    readonly_fields = ['costo_per_litro', 'get_consumo_detail']

    def get_consumo_display(self, obj):
        # Calcola consumo rispetto al rifornimento precedente
        precedente = RifornimentoCarburante.objects.filter(
            automezzo=obj.automezzo,
            data_rifornimento__lt=obj.data_rifornimento
        ).order_by('-data_rifornimento').first()
        
        if precedente:
            km_percorsi = obj.chilometri - precedente.chilometri
            if km_percorsi > 0:
                consumo = (obj.litri / km_percorsi) * 100
                if consumo < 6:
                    color = 'green'
                elif consumo <= 10:
                    color = 'orange'
                else:
                    color = 'red'
                return format_html(
                    '<span style="color: {};">{:.2f} L/100km</span>',
                    color, consumo
                )
        return '-'
    get_consumo_display.short_description = 'Consumo'

    def get_consumo_detail(self, obj):
        return self.get_consumo_display(obj)
    get_consumo_detail.short_description = 'Consumo Calcolato'


@admin.register(EventoAutomezzo)
class EventoAutomezzoAdmin(admin.ModelAdmin):
    """Admin per eventi automezzi"""
    list_display = [
        'automezzo', 'tipo', 'data_evento', 'get_descrizione_short',
        'costo', 'dipendente_coinvolto', 'get_stato_display'
    ]
    list_filter = ['tipo', 'risolto', 'data_evento', 'dipendente_coinvolto']
    search_fields = [
        'automezzo__targa', 'descrizione', 'dipendente_coinvolto__first_name',
        'dipendente_coinvolto__last_name'
    ]
    date_hierarchy = 'data_evento'
    list_select_related = ['automezzo', 'dipendente_coinvolto']

    def get_descrizione_short(self, obj):
        if len(obj.descrizione) > 50:
            return obj.descrizione[:50] + '...'
        return obj.descrizione
    get_descrizione_short.short_description = 'Descrizione'

    def get_stato_display(self, obj):
        if obj.risolto:
            return format_html('<span style="color: green;">✓ Risolto</span>')
        else:
            return format_html('<span style="color: red;">⚠ Aperto</span>')
    get_stato_display.short_description = 'Stato'


@admin.register(StatisticheAutomezzo)
class StatisticheAutomezzoAdmin(admin.ModelAdmin):
    """Admin per statistiche automezzi"""
    list_display = [
        'automezzo', 'consumo_medio', 'costo_km_carburante',
        'costo_manutenzioni_anno', 'ultimo_rifornimento', 'ultima_manutenzione'
    ]
    list_filter = ['ultimo_rifornimento', 'ultima_manutenzione']
    search_fields = ['automezzo__targa', 'automezzo__marca', 'automezzo__modello']
    readonly_fields = [
        'automezzo', 'consumo_medio', 'costo_km_carburante',
        'costo_manutenzioni_anno', 'ultimo_rifornimento', 'ultima_manutenzione'
    ]


# Configurazione admin site
admin.site.site_header = "Gestione Automezzi"
admin.site.site_title = "Automezzi Admin"
admin.site.index_title = "Pannello di Amministrazione Automezzi"