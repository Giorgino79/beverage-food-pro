# anagrafica/views_extra.py
# Views aggiuntive per funzionalità extra dell'anagrafica

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .models import Rappresentante, Cliente, Fornitore
from .forms import RappresentanteForm, ClienteForm, FornitoreForm


# ========== API AGGIUNTIVE ==========

@login_required
def rappresentanti_api(request):
    """API per autocompletamento rappresentanti (Select2)"""
    search = request.GET.get('term', '')
    
    rappresentanti = Rappresentante.objects.filter(
        Q(nome__icontains=search) |
        Q(ragione_sociale__icontains=search),
        attivo=True
    )[:10]
    
    results = []
    for r in rappresentanti:
        results.append({
            'id': r.id,
            'text': f"{r.nome} - {r.ragione_sociale}"
        })
    
    return JsonResponse({
        'results': results,
        'pagination': {'more': False}
    })


@login_required
def dashboard_stats_api(request):
    """API per statistiche dashboard in tempo reale"""
    stats = {
        'rappresentanti': {
            'totali': Rappresentante.objects.count(),
            'attivi': Rappresentante.objects.filter(attivo=True).count(),
        },
        'clienti': {
            'totali': Cliente.objects.count(),
            'attivi': Cliente.objects.filter(attivo=True).count(),
        },
        'fornitori': {
            'totali': Fornitore.objects.count(),
            'attivi': Fornitore.objects.filter(attivo=True).count(),
        },
        'today_stats': {
            'nuovi_clienti': Cliente.objects.filter(data_creazione__date=timezone.now().date()).count(),
            'nuovi_fornitori': Fornitore.objects.filter(data_creazione__date=timezone.now().date()).count(),
        }
    }
    
    return JsonResponse(stats)


@login_required
def validate_partita_iva(request):
    """Validazione AJAX partita IVA"""
    piva = request.GET.get('partita_iva', '').strip()
    
    if not piva:
        return JsonResponse({'valid': False, 'message': 'Partita IVA vuota'})
    
    if len(piva) != 11 or not piva.isdigit():
        return JsonResponse({'valid': False, 'message': 'Partita IVA deve essere di 11 cifre'})
    
    # Controllo checksum
    def validate_checksum(piva):
        total = 0
        for i, digit in enumerate(piva[:-1]):
            value = int(digit)
            if i % 2 == 0:
                value *= 2
                if value > 9:
                    value = (value // 10) + (value % 10)
            total += value
        check_digit = (10 - (total % 10)) % 10
        return int(piva[-1]) == check_digit
    
    if not validate_checksum(piva):
        return JsonResponse({'valid': False, 'message': 'Partita IVA non valida (checksum errato)'})
    
    # Verifica se già esiste
    tipo = request.GET.get('tipo', '')
    exclude_id = request.GET.get('exclude_id')
    
    query = Q(partita_iva=piva)
    if exclude_id:
        query &= ~Q(id=exclude_id)
    
    if tipo == 'rappresentante':
        exists = Rappresentante.objects.filter(query).exists()
    elif tipo == 'cliente':
        exists = Cliente.objects.filter(query).exists()
    elif tipo == 'fornitore':
        exists = Fornitore.objects.filter(query).exists()
    else:
        # Cerca in tutti i tipi
        exists = (Rappresentante.objects.filter(partita_iva=piva).exists() or
                 Cliente.objects.filter(partita_iva=piva).exists() or
                 Fornitore.objects.filter(partita_iva=piva).exists())
    
    if exists:
        return JsonResponse({'valid': False, 'message': 'Partita IVA già esistente'})
    
    return JsonResponse({'valid': True, 'message': 'Partita IVA valida'})


@login_required
def validate_codice_fiscale(request):
    """Validazione AJAX codice fiscale"""
    cf = request.GET.get('codice_fiscale', '').strip().upper()
    
    if not cf:
        return JsonResponse({'valid': False, 'message': 'Codice fiscale vuoto'})
    
    if len(cf) not in [11, 16]:
        return JsonResponse({'valid': False, 'message': 'Codice fiscale deve essere di 11 o 16 caratteri'})
    
    # Validazione formato
    import re
    if len(cf) == 16:
        pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
        if not re.match(pattern, cf):
            return JsonResponse({'valid': False, 'message': 'Formato codice fiscale non valido'})
    elif len(cf) == 11:
        if not cf.isdigit():
            return JsonResponse({'valid': False, 'message': 'Codice fiscale persona giuridica non valido'})
    
    # Verifica se già esiste
    tipo = request.GET.get('tipo', '')
    exclude_id = request.GET.get('exclude_id')
    
    query = Q(codice_fiscale=cf)
    if exclude_id:
        query &= ~Q(id=exclude_id)
    
    if tipo == 'rappresentante':
        exists = Rappresentante.objects.filter(query).exists()
    elif tipo == 'cliente':
        exists = Cliente.objects.filter(query).exists()
    elif tipo == 'fornitore':
        exists = Fornitore.objects.filter(query).exists()
    else:
        # Cerca in tutti i tipi
        exists = (Rappresentante.objects.filter(codice_fiscale=cf).exists() or
                 Cliente.objects.filter(codice_fiscale=cf).exists() or
                 Fornitore.objects.filter(codice_fiscale=cf).exists())
    
    if exists:
        return JsonResponse({'valid': False, 'message': 'Codice fiscale già esistente'})
    
    return JsonResponse({'valid': True, 'message': 'Codice fiscale valido'})


# ========== REPORTS PDF ==========

@staff_member_required
def rappresentanti_report_pdf(request):
    """Genera report PDF dei rappresentanti"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rappresentanti_report.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Titolo
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1,  # Centrato
        spaceAfter=30,
    )
    elements.append(Paragraph("Report Rappresentanti", title_style))
    elements.append(Spacer(1, 12))
    
    # Dati tabella
    data = [['Nome', 'Ragione Sociale', 'Email', 'Telefone', 'Zona', 'Clienti']]
    
    for r in Rappresentante.objects.filter(attivo=True).annotate(clienti_count=Count('clienti')):
        data.append([
            r.nome,
            r.ragione_sociale,
            r.email,
            r.telefono,
            r.zona or '-',
            str(r.clienti_count)
        ])
    
    # Creazione tabella
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response


@staff_member_required
def clienti_report_pdf(request):
    """Genera report PDF dei clienti"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="clienti_report.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Titolo
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1,
        spaceAfter=30,
    )
    elements.append(Paragraph("Report Clienti", title_style))
    elements.append(Spacer(1, 12))
    
    # Dati tabella
    data = [['Ragione Sociale', 'Città', 'Email', 'Rappresentante', 'Pagamento']]
    
    for c in Cliente.objects.filter(attivo=True).select_related('rappresentante'):
        data.append([
            c.ragione_sociale,
            c.città,
            c.email,
            c.rappresentante.nome if c.rappresentante else '-',
            c.get_pagamento_display()
        ])
    
    # Creazione tabella
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response


@staff_member_required
def fornitori_report_pdf(request):
    """Genera report PDF dei fornitori"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fornitori_report.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Titolo
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1,
        spaceAfter=30,
    )
    elements.append(Paragraph("Report Fornitori", title_style))
    elements.append(Spacer(1, 12))
    
    # Dati tabella
    data = [['Ragione Sociale', 'Città', 'Email', 'Categoria', 'Pagamento']]
    
    for f in Fornitore.objects.filter(attivo=True):
        data.append([
            f.ragione_sociale,
            f.città,
            f.email,
            f.categoria or '-',
            f.get_pagamento_display()
        ])
    
    # Creazione tabella
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response


# ========== IMPORT/EXPORT ==========

class ImportClientiView(TemplateView):
    """Vista per importazione clienti da CSV"""
    template_name = 'anagrafica/import/clienti.html'
    
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            messages.error(request, 'Nessun file selezionato')
            return self.get(request, *args, **kwargs)
        
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            messages.error(request, 'Il file deve essere in formato CSV')
            return self.get(request, *args, **kwargs)
        
        try:
            decoded_file = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
            
            created_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validazione dati obbligatori
                    if not row.get('ragione_sociale'):
                        raise ValueError('Ragione sociale obbligatoria')
                    
                    # Cerca rappresentante se specificato
                    rappresentante = None
                    if row.get('rappresentante'):
                        try:
                            rappresentante = Rappresentante.objects.get(
                                nome__icontains=row['rappresentante'],
                                attivo=True
                            )
                        except Rappresentante.DoesNotExist:
                            pass
                    
                    # Creazione cliente
                    cliente = Cliente.objects.create(
                        rappresentante=rappresentante,
                        ragione_sociale=row['ragione_sociale'],
                        indirizzo=row.get('indirizzo', ''),
                        cap=row.get('cap', ''),
                        città=row.get('città', ''),
                        provincia=row.get('provincia', ''),
                        partita_iva=row.get('partita_iva', ''),
                        codice_fiscale=row.get('codice_fiscale', ''),
                        telefono=row.get('telefono', ''),
                        email=row.get('email', ''),
                        pagamento=row.get('pagamento', '01'),
                    )
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Riga {row_num}: {str(e)}")
            
            if created_count > 0:
                messages.success(request, f'{created_count} clienti importati con successo')
            
            if error_count > 0:
                messages.error(request, f'{error_count} errori durante l\'importazione')
                for error in errors[:5]:  # Mostra solo i primi 5 errori
                    messages.error(request, error)
        
        except Exception as e:
            messages.error(request, f'Errore durante l\'importazione: {str(e)}')
        
        return self.get(request, *args, **kwargs)


class ImportFornitoriView(TemplateView):
    """Vista per importazione fornitori da CSV"""
    template_name = 'anagrafica/import/fornitori.html'
    
    def post(self, request, *args, **kwargs):
        # Implementazione simile a ImportClientiView
        pass


# ========== OPERAZIONI BATCH ==========

@staff_member_required
def attiva_multipli(request):
    """Attiva multipli record selezionati"""
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        ids = request.POST.getlist('ids')
        
        model_map = {
            'rappresentante': Rappresentante,
            'cliente': Cliente,
            'fornitore': Fornitore,
        }
        
        if tipo in model_map and ids:
            model_map[tipo].objects.filter(id__in=ids).update(attivo=True)
            messages.success(request, f'{len(ids)} {tipo}(i) attivati con successo')
    
    return redirect(request.META.get('HTTP_REFERER', 'anagrafica:dashboard'))


@staff_member_required
def disattiva_multipli(request):
    """Disattiva multipli record selezionati"""
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        ids = request.POST.getlist('ids')
        
        model_map = {
            'rappresentante': Rappresentante,
            'cliente': Cliente,
            'fornitore': Fornitore,
        }
        
        if tipo in model_map and ids:
            model_map[tipo].objects.filter(id__in=ids).update(attivo=False)
            messages.success(request, f'{len(ids)} {tipo}(i) disattivati con successo')
    
    return redirect(request.META.get('HTTP_REFERER', 'anagrafica:dashboard'))


@staff_member_required
def elimina_multipli(request):
    """Elimina multipli record selezionati"""
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        ids = request.POST.getlist('ids')
        
        model_map = {
            'rappresentante': Rappresentante,
            'cliente': Cliente,
            'fornitore': Fornitore,
        }
        
        if tipo in model_map and ids:
            # Verifica dipendenze prima dell'eliminazione
            count = len(ids)
            
            if tipo == 'rappresentante':
                # Verifica se hanno clienti
                with_clients = Rappresentante.objects.filter(
                    id__in=ids, 
                    clienti__isnull=False
                ).distinct().count()
                
                if with_clients > 0:
                    messages.error(request, f'{with_clients} rappresentanti hanno clienti associati')
                    return redirect(request.META.get('HTTP_REFERER', 'anagrafica:dashboard'))
            
            # Eliminazione
            model_map[tipo].objects.filter(id__in=ids).delete()
            messages.success(request, f'{count} {tipo}(i) eliminati con successo')
    
    return redirect(request.META.get('HTTP_REFERER', 'anagrafica:dashboard'))