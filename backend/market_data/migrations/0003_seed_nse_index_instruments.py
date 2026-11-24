from django.db import migrations


NSE_INDEX_INSTRUMENTS = {
    "NIFTY": "NIFTY 50",
    "BANKNIFTY": "NIFTY BANK",
    "FINNIFTY": "NIFTY FINANCIAL SERVICES",
    "MIDCPNIFTY": "NIFTY MIDCAP SELECT",
    "NIFTYNXT50": "NIFTY NEXT 50",
}


def seed_nse_index_instruments(apps, schema_editor):
    Instrument = apps.get_model("market_data", "Instrument")
    database = schema_editor.connection.alias

    for symbol, name in NSE_INDEX_INSTRUMENTS.items():
        Instrument.objects.using(database).get_or_create(
            symbol=symbol,
            defaults={
                "name": name,
                "exchange": "NSE",
                "asset_class": "INDEX",
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("market_data", "0002_instrument_asset_class_instrument_exchange"),
    ]

    operations = [
        migrations.RunPython(
            seed_nse_index_instruments,
            migrations.RunPython.noop,
        ),
    ]
