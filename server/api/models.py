# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# top down view of 
CRYPTO_TABLES = ['btc_gbp', 'eth_gbp', 'sol_gbp', 'sui_gbp']

# Define your abstract base class once
class BaseCryptoModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.BigIntegerField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    low = models.FloatField(blank=True, null=True)
    open = models.FloatField(blank=True, null=True)
    volumefrom = models.FloatField(blank=True, null=True)
    volumeto = models.FloatField(blank=True, null=True)
    close = models.FloatField(blank=True, null=True)
    conversionType = models.TextField(db_column='conversionType', blank=True, null=True)
    conversionSymbol = models.TextField(db_column='conversionSymbol', blank=True, null=True)

    class Meta:
        abstract = True

# Dynamic class registry (optional, useful for introspection or router wiring)
models_crypto_classes = {}

# Create crypto classes dynamically
for table in CRYPTO_TABLES:
    class_name = ''.join(part.capitalize() for part in table.split('_'))  # e.g. 'btc_gbp' → 'BtcGbp'

    model_class = type(
        class_name,
        (BaseCryptoModel,),
        {
            '__module__': __name__,  # important for Django internals
            'Meta': type('Meta', (), {
                'managed': True,
                'db_table': table
            })
        }
    )

    models_crypto_classes[class_name] = model_class
    globals()[class_name] = model_class  # make it accessible globally if needed
    
