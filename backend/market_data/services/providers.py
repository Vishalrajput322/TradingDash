from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


def get_market_data_provider(exchange: str):
    """Instantiate the configured provider for an exchange.

    Providers must expose ``option_chain(symbol, expiry=None,
    asset_class="INDEX")``. A provider used for futures ingestion must also
    expose ``futures_quote(symbol, expiry=None)``.
    """
    exchange = exchange.strip().upper()
    provider_path = settings.MARKET_DATA_PROVIDERS.get(exchange)
    if not provider_path:
        raise ImproperlyConfigured(
            f"No market data provider is configured for {exchange}."
        )

    provider_class = import_string(provider_path)
    return provider_class()


def parse_expiry_date(value: str) -> date:
    for date_format in ("%d-%b-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue
    raise ValueError(
        f"Unsupported provider expiry date '{value}'; use DD-Mon-YYYY or YYYY-MM-DD."
    )
