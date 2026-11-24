from django.contrib import admin
from options.models import FuturesSnapshot, OptionChainSnapshot

admin.site.register(FuturesSnapshot)
admin.site.register(OptionChainSnapshot)
