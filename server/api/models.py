# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BaseCryptoModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.BigIntegerField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    low = models.FloatField(blank=True, null=True)
    open = models.FloatField(blank=True, null=True)
    volumefrom = models.FloatField(blank=True, null=True)
    volumeto = models.FloatField(blank=True, null=True)
    close = models.FloatField(blank=True, null=True)
    conversionType = models.TextField(db_column='conversionType', blank=True, null=True)  # Field name made lowercase.
    conversionSymbol = models.TextField(db_column='conversionSymbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        abstract = True

class BtcGbp(BaseCryptoModel):
    class Meta:
        managed = True
        db_table = 'btc_gbp'

class EthGbp(BaseCryptoModel):
    class Meta:
        managed = True
        db_table = 'eth_gbp'

class SolGbp(BaseCryptoModel):
    class Meta:
        managed = True
        db_table = 'sol_gbp'

class SuiGbp(BaseCryptoModel):
    class Meta:
        managed = True
        db_table = 'sui_gbp'
    
