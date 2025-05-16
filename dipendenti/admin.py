from django.contrib import admin
from .models import Dipendente, Giornata, AllegatoDipendente

admin.site.register(Dipendente)
admin.site.register(Giornata)
admin.site.register(AllegatoDipendente)