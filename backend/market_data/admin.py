from django.contrib import admin
from market_data.models import Instrument, OptionExpiry

admin.site.register(Instrument)
admin.site.register(OptionExpiry)
