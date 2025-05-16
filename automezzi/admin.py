from django.contrib import admin
from .models import (
    TipoCarburante,
    Automezzo,
    DocumentoAutomezzo,
    Manutenzione,
    RifornimentoCarburante,
    EventoAutomezzo,
    StatisticheAutomezzo
)

admin.site.register(TipoCarburante)
admin.site.register(Automezzo)
admin.site.register(DocumentoAutomezzo)
admin.site.register(Manutenzione)
admin.site.register(RifornimentoCarburante)
admin.site.register(EventoAutomezzo)
admin.site.register(StatisticheAutomezzo)