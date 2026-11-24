from django.db import models

from django.db import models


class Instrument(models.Model):
    class Exchange(models.TextChoices):
        NSE = "NSE", "National Stock Exchange"
        MCX = "MCX", "Multi Commodity Exchange"

    class AssetClass(models.TextChoices):
        INDEX = "INDEX", "Index"
        EQUITY = "EQUITY", "Equity"
        COMMODITY = "COMMODITY", "Commodity"

    symbol = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    exchange = models.CharField(
        max_length=3,
        choices=Exchange.choices,
        default=Exchange.NSE,
        db_index=True,
    )
    asset_class = models.CharField(
        max_length=10,
        choices=AssetClass.choices,
        default=AssetClass.INDEX,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol


class OptionExpiry(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)