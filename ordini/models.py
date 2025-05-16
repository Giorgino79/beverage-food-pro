from django.db import models
from decimal import Decimal, InvalidOperation

class Categoria(models.Model):
    nome_categoria=models.CharField(max_length=200)
    icona=models.ImageField(upload_to='media/categorie', blank=True, null=True)

    def __str__(self):
        return f'{self.nome_categoria}'


class Prodotto(models.Model):
    class Misura(models.TextChoices):
        bottiglia='bottiglie','Vendita a bottiglia'
        kilo='kilo','Vendita al peso'
        litro='litro','Vendita al litro'
        confezione='confezione', 'Vendita a confezione'
    class Aliquota(models.TextChoices):
        quattro='4%','Iva al 4%'
        dieci='10%','Iva al 10%'
        ventidue='22%','Iva al 22%'
    categoria=models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nome_prodotto=models.CharField(max_length=200)
    ean=models.IntegerField()
    misura=models.CharField(max_length=15, choices=Misura.choices, default='confezione')
    aliquota_iva=models.CharField(max_length=10, choices=Aliquota.choices, default='22%')

    def __str__(self):
        return f'{self.nome_prodotto}'

    def get_aliquota_iva_numerica(self):
        """Restituisce l'aliquota IVA come valore decimale."""
        valore = self.aliquota_iva.replace('%', '')
        try:
            return float(valore) / 100.0
        except ValueError:
            return 0.0


class Ordine(models.Model):
    class Misura(models.TextChoices):
        bottiglia='bottiglie','Vendita a bottiglia'
        kilo='kilo','Vendita al peso'
        litro='litro','Vendita al litro'
        confezione='confezione', 'Vendita a confezione'
    prodotto=models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    fornitore=models.ForeignKey('anagrafica.Fornitore', on_delete=models.CASCADE)
    misura=models.CharField(max_length=50, choices=Misura.choices, default='confezione')
    pezzi_per_confezione = models.FloatField(null=True, blank=True)
    quantita_ordinata = models.IntegerField()
    prezzo_unitario_ordine = models.DecimalField(max_digits=10, decimal_places=2)
    prezzo_totale_ordine = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    totale_ordine_ivato = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    pdf_ordine = models.FileField(upload_to='media/ordini_pdf/', blank=True, null=True)
    data_invio_ordine = models.DateField(null=True, blank=True)
    data_arrivo_previsto = models.DateField(null=True, blank=True)
    data_ricezione_ordine = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Ordine {self.id} - {self.prodotto.nome_prodotto}"

    def save(self, *args, **kwargs):
        if self.prodotto and self.quantita_ordinata is not None and self.prezzo_unitario_ordine is not None:
            if self.misura == Ordine.Misura.confezione and self.pezzi_per_confezione is not None:
                try:
                    pezzi_per_confezione_decimal = Decimal(str(self.pezzi_per_confezione))
                    self.prezzo_totale_ordine = self.prezzo_unitario_ordine * pezzi_per_confezione_decimal * self.quantita_ordinata
                except InvalidOperation:
                    print("Errore: Impossibile convertire pezzi_per_confezione in Decimal nel modello.")
                    self.prezzo_totale_ordine = Decimal('0.00')
            else:
                self.prezzo_totale_ordine = self.prezzo_unitario_ordine * self.quantita_ordinata

            aliquota_iva_numerica = self.prodotto.get_aliquota_iva_numerica()
            if not isinstance(aliquota_iva_numerica, Decimal):
                aliquota_iva_decimal = Decimal(str(aliquota_iva_numerica))
            else:
                aliquota_iva_decimal = aliquota_iva_numerica

            self.totale_ordine_ivato = self.prezzo_totale_ordine * (Decimal('1.0') + aliquota_iva_decimal)

        super().save(*args, **kwargs)


class Ricezione(models.Model):
    ordine = models.OneToOneField(Ordine, on_delete=models.CASCADE, related_name='ricezione')
    data_ricezione = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ricezione Ordine {self.ordine.id}"


class ProdottoRicevuto(models.Model):
    ricezione = models.ForeignKey(Ricezione, on_delete=models.CASCADE, related_name='prodotti_ricevuti')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita_ricevuta = models.IntegerField()
    data_scadenza = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.prodotto.nome_prodotto} (Ricezione {self.ricezione.ordine.id})"


class Magazzino(models.Model):
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita_in_magazzino = models.IntegerField(default=0)
    data_scadenza = models.DateField(null=True, blank=True)
    data_ingresso = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('prodotto', 'data_scadenza')

    def __str__(self):
        return f"{self.prodotto.nome_prodotto} - Scadenza: {self.data_scadenza if self.data_scadenza else 'N/A'} - Qta: {self.quantita_in_magazzino}"
