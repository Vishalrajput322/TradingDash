from django.db import models
from market_data.models import Instrument, OptionExpiry


class OptionChainSnapshot(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    expiry = models.ForeignKey(OptionExpiry, on_delete=models.CASCADE)
    strike = models.DecimalField(max_digits=10, decimal_places=2)
    call_oi = models.BigIntegerField()
    put_oi = models.BigIntegerField()
    call_oi_change = models.BigIntegerField()
    put_oi_change = models.BigIntegerField()
    call_volume = models.BigIntegerField()
    put_volume = models.BigIntegerField()
    call_ltp = models.DecimalField(max_digits=12, decimal_places=2)
    put_ltp = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(db_index=True)
   
    class Meta:
        indexes = [models.Index(fields=["instrument", "timestamp"]),]