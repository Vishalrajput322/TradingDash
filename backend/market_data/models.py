from django.db import models

from django.db import models


class Instrument(models.Model):
    symbol = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol


class OptionExpiry(models.Model):
    instrument = models.ForeignKey(Instrument,on_delete=models.CASCADE)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)