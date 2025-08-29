# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

CRYPTOS = ['SUI', 'ETH', 'SOL', 'BTC']
FIATS = ['GBP', 'USD', 'EUR']

class CurrencyPair(models.Model):
    base_code = models.CharField(max_length=10)   # e.g., BTC
    quote_code = models.CharField(max_length=10)  # e.g., USD

    class Meta:
        db_table = 'currency_pair'
        unique_together = ('base_code', 'quote_code')

    def __str__(self):
        return f"{self.base_code}/{self.quote_code}"

class OHLCV(models.Model):
    pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE)
    pair_name = models.CharField(max_length=7, default="unknown")
    timestamp = models.BigIntegerField()
    open = models.DecimalField(max_digits=18, decimal_places=3)
    high = models.DecimalField(max_digits=18, decimal_places=3)
    low = models.DecimalField(max_digits=18, decimal_places=3)
    close = models.DecimalField(max_digits=18, decimal_places=3)
    volumeFrom = models.DecimalField(max_digits=30, decimal_places=3)
    volumeTo = models.DecimalField(max_digits=30, decimal_places=3)

    class Meta:
        db_table = 'ohlcv_hourly'
        unique_together = ('pair', 'timestamp')
        indexes = [
            models.Index(fields=['pair', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.pair} | {self.timestamp}"