from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO, StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from django.http import HttpResponse
import csv
import datetime
import locale
import os
from django import forms
from django.utils import timezone
from django.template.loader import render_to_string
from xhtml2pdf import pisa

# Classe DateInput per i campi data nei form
class DateInput(forms.DateInput):
    input_type = "date"

# Funzione per ottenere data e ora formattate per PDF
def get_formatted_datetime_for_pdf():
    """
    Restituisce un dizionario con data e ora formattati correttamente
    per l'uso nei template PDF, usando il fuso orario italiano.
    """
    from django.utils import timezone
    import pytz
    
    # Ottieni l'ora corrente in UTC
    now_utc = timezone.now()
    
    # Converti nell'ora italiana (Europe/Rome)
    italian_tz = pytz.timezone('Europe/Rome')
    now_italy = now_utc.astimezone(italian_tz)
    
    return {
        'data_formattata': now_italy.strftime('%d/%m/%Y'),
        'ora_formattata': now_italy.strftime('%H:%M'),
        'data': now_italy,  # Manteniamo anche l'oggetto data originale
        'today': now_italy.date()  # Utile per i confronti nelle date
    }

# Funzione per inviare email
def invia_mail(subject, body, to_emails, cc_emails=None, bcc_emails=None, attachments=None, from_email=None):
    """
    Funzione generica per inviare email con supporto per allegati.

    Args:
        subject (str): L'oggetto dell'email.
        body (str): Il corpo (testo semplice) dell'email.
        to_emails (list): Una lista di indirizzi email dei destinatari principali.
        cc_emails (list, optional): Una lista di indirizzi email in copia conoscenza. Defaults to None.
        bcc_emails (list, optional): Una lista di indirizzi email in copia conoscenza nascosta. Defaults to None.
        attachments (list, optional): Una lista di tuple nel formato ('nome_file', contenuto_file, 'tipo_mime'). Defaults to None.
        from_email (str, optional): L'indirizzo email del mittente. Se None, usa DEFAULT_FROM_EMAIL da settings. Defaults to None.
    """
    if not settings.EMAIL_HOST_USER:
        print("Errore: EMAIL_HOST_USER non configurato in settings.py")
        return False

    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

    email = EmailMessage(subject, body, from_email, to_emails, bcc=bcc_emails)
    email.content_subtype = 'html'  # Specifica che il corpo è HTML

    if cc_emails:
        email.cc = cc_emails
    if attachments:
        for filename, content, mimetype in attachments:
            email.attach(filename, content, mimetype)

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
        return False

# Funzione aggiornata per produrre PDF con template base e logo
def produci_pdf(html_template, context={}, filename="documento.pdf"):
    """
    Funzione per produrre un documento PDF in memoria da un template HTML,
    utilizzando un template base con logo e footer aziendali.

    Args:
        html_template (str): Il percorso del template HTML da renderizzare.
        context (dict, optional): Il contesto da passare al template. Defaults to {}.
        filename (str, optional): Il nome del file PDF da scaricare. Defaults to "documento.pdf".

    Returns:
        BytesIO: Un oggetto BytesIO contenente il PDF.
    """
    # Aggiungi al contesto le informazioni di base
    base_context = {
        # Percorso assoluto per il logo
        'logo_path': os.path.join(settings.BASE_DIR, 'static', 'logonuovo.jpeg'),
        'document_title': context.get('titolo', 'Documento'),
        'company_name': 'La Tua Azienda',
        'company_address': 'Via dell\'Azienda, 123 - 00123 Roma',
        'company_email': 'info@tuaazienda.it',
        'company_phone': '+39 06 12345678',
        'company_vat': 'P.IVA: 12345678901'
    }
    
    # Log per il debug
    print(f"Percorso logo: {base_context['logo_path']}")
    print(f"Il file esiste: {os.path.exists(base_context['logo_path'])}")
    
    # Aggiorna il contesto con le informazioni temporali
    datetime_info = get_formatted_datetime_for_pdf()
    base_context.update(datetime_info)
    
    # Aggiorna il contesto con i parametri forniti
    base_context.update(context)
    
    # Renderizza il template HTML
    html = render_to_string(html_template, base_context)
    
    # Crea il PDF
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)
    
    if not pdf.err:
        # Riposiziona il puntatore all'inizio del buffer
        result.seek(0)
        return result
    
    print(f"Errore nella generazione del PDF: {pdf.err}")
    return None

# Funzione per produrre CSV
def produci_csv(data, filename="dati.csv"):
    """
    Funzione generica per produrre un file CSV in memoria.

    Args:
        data (list of list): Una lista di liste, dove ogni lista rappresenta una riga del CSV.
                             La prima lista dovrebbe contenere le intestazioni delle colonne.
        filename (str, optional): Il nome del file CSV da scaricare. Defaults to "dati.csv".

    Returns:
        HttpResponse: Un oggetto HttpResponse con il CSV come allegato.
    """
    buffer = StringIO()
    writer = csv.writer(buffer)

    for row in data:
        writer.writerow(row)

    csv_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(csv_data)

    return response

# Impostazione del locale italiano
try:
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Italian_Italy.1252')  # Per Windows
    except locale.Error:
        print("Impossibile impostare il locale italiano. Usando il locale predefinito.")

# Funzione per ottenere data e ora correnti
def get_current_datetime_data():
    now = datetime.datetime.now()
    today_date = now.strftime("%d %B %Y")  # Es: 20 Aprile 2025
    today_day = now.strftime("%A")         # Es: Domenica
    current_time = now.strftime("%H:%M")
    return {
        'today_date': today_date,
        'today_day': today_day,
        'current_time': current_time,
        'today': now.date()  # Utile per i confronti nelle date
    }