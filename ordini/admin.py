from django.contrib import admin
from .models import Categoria,Prodotto,Ordine,Magazzino,Ricezione,ProdottoRicevuto

admin.site.register(Categoria)
admin.site.register(Prodotto)
admin.site.register(Ordine)
admin.site.register(Magazzino)
admin.site.register(Ricezione)
admin.site.register(ProdottoRicevuto)
