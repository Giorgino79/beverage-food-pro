# Gestione Automezzi Django

Questa app Django permette la gestione di una flotta di automezzi aziendali, con anagrafiche, eventi, manutenzioni, rifornimenti e dashboard riassuntiva.

## Struttura

```
automezzi/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
├── templates/
│   └── automezzi/
│       ├── automezzo_list.html
│       ├── automezzo_detail.html
│       ├── automezzo_form.html
│       ├── automezzo_confirm_delete.html
│       ├── manutenzione_list.html
│       ├── manutenzione_detail.html
│       ├── manutenzione_form.html
│       ├── manutenzione_confirm_delete.html
│       ├── rifornimento_list.html
│       ├── rifornimento_detail.html
│       ├── rifornimento_form.html
│       ├── rifornimento_confirm_delete.html
│       ├── evento_list.html
│       ├── evento_detail.html
│       ├── evento_form.html
│       ├── evento_confirm_delete.html
│       └── dashboard.html
└── static/
    └── automezzi/
        └── (js/css)
```

## Funzionalità

- **CRUD Automezzi**: anagrafica, libretto, assicurazione, assegnazione.
- **CRUD Manutenzioni**: storico, allegati, stato.
- **CRUD Rifornimenti**: storico, scontrini, km.
- **CRUD Eventi**: incidenti, furti, fermi, allegati, coinvolgimento personale.
- **Dashboard**: riepilogo rapido e ultimi movimenti.

## Modelli principali

- `Automezzo`
- `Manutenzione`
- `Rifornimento`
- `EventoAutomezzo`

## Views principali

- Tutte le operazioni CRUD con Class Based Views.
- Navigazione tramite URL RESTful.
- Dashboard come TemplateView.

## Esempio URL RESTful

- `/automezzi/` – lista automezzi
- `/automezzi/nuovo/` – nuovo automezzo
- `/automezzi/23/` – dettaglio automezzo 23
- `/automezzi/23/manutenzioni/` – manutenzioni automezzo 23
- `/manutenzioni/` – tutte le manutenzioni
- `/automezzi/23/eventi/` – eventi su automezzo 23
- `/` – dashboard

## Dipendenze consigliate

- **Django** >= 3.2
- **django-crispy-forms** (opzionale, per form Bootstrap)
- **Bootstrap** (opzionale, per una UI più moderna)

## Esempio di impostazione base per crispy-forms e Bootstrap

Nel tuo `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'crispy_forms',
    'crispy_bootstrap5',  # o 'crispy_bootstrap4'
]
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

Nel tuo `base.html`:
```html
{% load static %}
{% load crispy_forms_tags %}
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>Gestione Automezzi</title>
    <link rel="stylesheet" href="{% static 'automezzi/bootstrap.min.css' %}">
</head>
<body>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

Nei template dei form, sostituisci  
`{{ form.as_p }}`  
con  
`{% crispy form %}`

## Note per lo sviluppo

- Ricorda di gestire `MEDIA_ROOT` e `MEDIA_URL` in settings.py per gli upload di file.
- Personalizza le autorizzazioni secondo le tue esigenze (es: chi può modificare cosa).
- Puoi estendere la dashboard con grafici (es. Chart.js) o filtri rapidi.

---

> **Consiglio:**  
> Se riscontri lentezza/timeout, apri pure una nuova sessione: i tuoi prompt e la cronologia sono nel tuo ambiente locale, non perderai i file già generati.
