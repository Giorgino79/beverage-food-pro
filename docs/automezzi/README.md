# README – Appunti e Convenzioni Copilot per `automezzi`

Questo file raccoglie i punti salienti, decisioni e best practice emerse dalle discussioni con Copilot e dallo sviluppo dell’app `automezzi`.

---

## 1. Convenzioni sui Template

- Tutti i template delle manutenzioni si trovano in `templates/automezzi/manutenzioni/`.
- Nomi template principali:
  - `nuovo.html` — creazione manutenzione
  - `modifica.html` — modifica manutenzione
  - `elimina.html` — eliminazione manutenzione
  - `dettaglio.html` — dettaglio manutenzione
  - `elenco.html` — elenco manutenzioni per automezzo
  - `elenco_globale.html` — elenco globale di tutte le manutenzioni
  - `completa.html` — conferma completamento manutenzione
- Nei template, usare `{% load humanize %}` per formattazioni numeriche e date.
- Per i form utilizzare `crispy_forms` e Bootstrap per una migliore UX.

---

## 2. App e Librerie Django

- Aggiungere `'django.contrib.humanize'` a `INSTALLED_APPS` in `settings.py` per abilitare i filtri come `intcomma`, `floatformat`, ecc.
- Non è necessario installare pacchetti esterni per i filtri humanize, fanno parte di Django.

---

## 3. Gestione delle Discussioni Copilot

- Copilot **non ha memoria persistente**: le discussioni non sono salvate tra una sessione e l’altra.
- Soluzioni, template, scelte progettuali e appunti vanno salvati in file `.md` come questo, da tenere nella cartella dell’app (`docs/automezzi/`).
- Consigliato nominare i file degli appunti secondo la data o l’argomento (es: `16052025.md`).

**Esempio struttura:**
```
docs/
  automezzi/
    README.md
    16052025.md
  altro_app/
    data.md
```

---

## 4. Best Practice

- Annotare in questo README (o in file giornalieri/tematici) soluzioni custom, scelte tecniche, workaround.
- Aggiornare il file ogni volta che si stabilisce una nuova convenzione o si prende una decisione progettuale importante.

---

## 5. Esempi Utili

- **Formattazione costo:**
  ```django
  {{ manutenzione.costo|floatformat:2 }} €
  ```
- **Link a dettaglio automezzo:**
  ```django
  {% url 'automezzi:dettaglio' manutenzione.automezzo.pk %}?sezione=manutenzioni
  ```
- **Badge completamento:**
  ```django
  {% if manutenzione.completata %}
    <span class="badge bg-success">Sì</span>
  {% else %}
    <span class="badge bg-warning text-dark">No</span>
  {% endif %}
  ```

---

> _Mantieni aggiornato questo README e aggiungi note specifiche per non perdere memoria delle buone pratiche o delle decisioni prese!_