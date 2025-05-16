from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory
from .forms import ProdottoForm, OrdineForm, RicezioneForm, ProdottoRicevutoForm, CategoriaForm
from .models import Prodotto, Ordine, Ricezione, ProdottoRicevuto, Magazzino, Categoria
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from django.core.mail import EmailMessage
import datetime
from django.contrib.auth.decorators import login_required


def nuova_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria creata con successo.')
            return redirect('ordini:lista_categorie')  # Dovrai definire questa URL
        else:
            messages.error(request, 'Si è verificato un errore durante la creazione della categoria.')
    else:
        form = CategoriaForm()
    return render(request, 'ordini/nuova_categoria.html', {'form': form})

def lista_categorie(request):
    categorie = Categoria.objects.all()
    return render(request, 'ordini/lista_categorie.html', {'categorie': categorie})

def genera_pdf_ordine(ordine):
    template_path = 'ordini/pdf_ordine.html'
    context = {'ordine': ordine, 'MEDIA_ROOT': settings.MEDIA_ROOT, 'MEDIA_URL': settings.MEDIA_URL}
    html = render_to_string(template_path, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result
    return None

def invia_email_ordine_fornitore(ordine_id):
    try:
        ordine = Ordine.objects.get(pk=ordine_id)
        fornitore = ordine.fornitore

        subject = f"Nuovo Ordine - Riferimento Ordine: {ordine.id}"
        body = render_to_string('email/ordine_fornitore.html', {'ordine': ordine, 'fornitore': fornitore})

        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [fornitore.email]
        )

        pdf_file = genera_pdf_ordine(ordine)
        # if pdf_file:
        #     email.attach(f"ordine_{ordine.id}.pdf", pdf_file.getvalue(), 'application/pdf')
        #     # Salva il PDF nel campo pdf_ordine
        #     ordine.pdf_ordine.save(f"ordine_{ordine.id}.pdf", pdf_file, save=False)
        #     ordine.save() # Salva l'ordine con il PDF allegato

        email.send()
        return True
    except Ordine.DoesNotExist:
        print(f"Errore: Ordine con ID {ordine_id} non trovato.")
        return False
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
        return False

# Views per Prodotto
def lista_prodotti(request):
    prodotti = Prodotto.objects.all()
    return render(request, 'ordini/prodotti/lista_prodotti.html', {'prodotti': prodotti})

def nuovo_prodotto(request):
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prodotto creato con successo.')
            return redirect('ordini:lista_prodotti')
        else:
            messages.error(request, 'Si è verificato un errore durante la creazione del prodotto.')
    else:
        form = ProdottoForm()
    return render(request, 'ordini/prodotti/nuovo_prodotto.html', {'form': form})

def modifica_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, pk=pk)
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES, instance=prodotto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prodotto modificato con successo.')
            return redirect('ordini:lista_prodotti')
        else:
            messages.error(request, 'Si è verificato un errore durante la modifica del prodotto.')
    else:
        form = ProdottoForm(instance=prodotto)
    return render(request, 'ordini/prodotti/modifica_prodotto.html', {'form': form, 'prodotto': prodotto})

def elimina_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, pk=pk)
    if request.method == 'POST':
        prodotto.delete()
        messages.success(request, f'Prodotto "{prodotto.nome_prodotto}" eliminato con successo.')
        return redirect('ordini:lista_prodotti')
    return render(request, 'ordini/prodotti/elimina_prodotto.html', {'prodotto': prodotto})

# Views per Ordine
def lista_ordini(request):
    ordini = Ordine.objects.all()
    return render(request, 'ordini/lista_ordini.html', {'ordini': ordini})

def lista_ordini_da_ricevere(request):
    ordini = Ordine.objects.filter(data_ricezione_ordine__isnull=True)
    return render(request, 'ordini/lista_ordini_da_ricevere.html', {'ordini': ordini})

def lista_ordini_ricevuti(request):
    ordini = Ordine.objects.filter(data_ricezione_ordine__isnull=False)
    return render(request, 'ordini/lista_ordini_ricevuti.html', {'ordini': ordini})

def nuovo_ordine(request):
    if request.method == 'POST':
        form = OrdineForm(request.POST)
        if form.is_valid():
            ordine = form.save()
            inviato = invia_email_ordine_fornitore(ordine.id) # Chiama la funzione per inviare l'email
            if inviato:
                messages.success(request, f'Ordine {ordine.id} creato e inviato via email al fornitore.')
            else:
                messages.warning(request, f'Ordine {ordine.id} creato, ma si è verificato un errore durante l\'invio dell\'email.')
            return redirect('ordini:lista_ordini')
        else:
            messages.error(request, 'Si è verificato un errore durante la creazione dell\'ordine.')
    else:
        form = OrdineForm()
    return render(request, 'ordini/nuovo_ordine.html', {'form': form})

def modifica_ordine(request, pk):
    ordine = get_object_or_404(Ordine, pk=pk)
    if request.method == 'POST':
        form = OrdineForm(request.POST, instance=ordine)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ordine {ordine.id} modificato con successo.')
            return redirect('ordini:lista_ordini')
        else:
            messages.error(request, 'Si è verificato un errore durante la modifica dell\'ordine.')
    else:
        form = OrdineForm(instance=ordine)
    return render(request, 'ordini/modifica_ordine.html', {'form': form, 'ordine': ordine})

def conferma_ordine(request, ordine_id):
    ordine = get_object_or_404(Ordine, pk=ordine_id)
    if request.method == 'POST':
        ordine.data_invio_ordine = datetime.date.today()
        ordine.save()
        inviato = invia_email_ordine_fornitore(ordine.id)
        if inviato:
            messages.success(request, f"Ordine {ordine.id} confermato e inviato via email al fornitore.")
        else:
            messages.warning(request, f"Ordine {ordine.id} confermato, ma si è verificato un errore durante l'invio dell'email.")
        return redirect('ordini:lista_ordini')
    else:
        context = {'ordine': ordine}
        return render(request, 'ordini/conferma_ordine.html', context)

def elimina_ordine(request, pk):
    ordine = get_object_or_404(Ordine, pk=pk)
    if request.method == 'POST':
        ordine.delete()
        messages.success(request, f'Ordine {ordine.id} eliminato con successo.')
        return redirect('ordini:lista_ordini')
    return render(request, 'ordini/elimina_ordine.html', {'ordine': ordine})

def ricevi_ordine(request, ordine_id):
    ordine = get_object_or_404(Ordine, pk=ordine_id)

    # Crea un formset pre-popolato per i prodotti ricevuti
    extra_forms = 1 if ordine.misura == Ordine.Misura.confezione else ordine.quantita_ordinata
    ProdottoRicevutoFormSet = modelformset_factory(ProdottoRicevuto, form=ProdottoRicevutoForm, extra=extra_forms)

    initial_data = []
    if ordine.misura == Ordine.Misura.confezione:
        initial_data.append({'prodotto': ordine.prodotto})
    else:
        for _ in range(ordine.quantita_ordinata):
            initial_data.append({'prodotto': ordine.prodotto})

    ricezione_form = RicezioneForm(initial={'ordine': ordine})
    prodotti_ricevuti_formset = ProdottoRicevutoFormSet(request.POST if request.POST else None, initial=initial_data, queryset=ProdottoRicevuto.objects.none())

    if request.method == 'POST':
        ricezione_form = RicezioneForm(request.POST, initial={'ordine': ordine})
        prodotti_ricevuti_formset = ProdottoRicevutoFormSet(request.POST, queryset=ProdottoRicevuto.objects.none())
        if ricezione_form.is_valid() and prodotti_ricevuti_formset.is_valid():
            ricezione = ricezione_form.save()
            ordine.data_ricezione_ordine = datetime.date.today()
            ordine.save()
            for form in prodotti_ricevuti_formset:
                if form.cleaned_data:
                    prodotto_ricevuto = form.save(commit=False)
                    prodotto_ricevuto.ricezione = ricezione
                    prodotto_ricevuto.save()
                    # Aggiorna il magazzino
                    magazzino_entry, created = Magazzino.objects.get_or_create(
                        prodotto=prodotto_ricevuto.prodotto,
                        data_scadenza=prodotto_ricevuto.data_scadenza,
                        defaults={'quantita_in_magazzino': 0}
                    )
                    magazzino_entry.quantita_in_magazzino += prodotto_ricevuto.quantita_ricevuta
                    magazzino_entry.save()
            messages.success(request, f"Ordine {ordine.id} ricevuto e magazzino aggiornato.")
            return redirect('ordini:lista_ordini_ricevuti')
        else:
            messages.error(request, "Si è verificato un errore durante la ricezione dell'ordine.")

    context = {
        'ordine': ordine,
        'ricezione_form': ricezione_form,
        'prodotti_ricevuti_formset': prodotti_ricevuti_formset,
    }
    return render(request, 'ordini/ricevi_ordine.html', context)

def visualizza_magazzino(request):
    inventario = Magazzino.objects.all().order_by('prodotto__nome_prodotto', 'data_scadenza')
    return render(request, 'ordini/visualizza_magazzino.html', {'inventario': inventario})
