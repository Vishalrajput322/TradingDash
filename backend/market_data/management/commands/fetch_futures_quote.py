from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from requests import RequestException

from market_data.models import Instrument
from market_data.services.providers import get_market_data_provider
from options.services.futures_snapshot_service import FuturesSnapshotService


class Command(BaseCommand):
    help = "Fetch and store one futures quote using the configured exchange provider"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", required=True)
        parser.add_argument("--expiry", required=True, help="Contract expiry in YYYY-MM-DD format")

    def handle(self, *args, **options):
        symbol = options["symbol"].strip().upper()
        expiry = options["expiry"].strip()
        try:
            instrument = Instrument.objects.get(symbol=symbol, is_active=True)
        except Instrument.DoesNotExist as exc:
            raise CommandError(f"Active instrument not found for '{symbol}'.") from exc

        try:
            provider = get_market_data_provider(instrument.exchange)
            quote = provider.futures_quote(symbol, expiry=expiry)
            snapshot = FuturesSnapshotService.save_quote(instrument, quote)
        except (
            AttributeError,
            ImproperlyConfigured,
            RequestException,
            ValueError,
            TypeError,
        ) as exc:
            raise CommandError(
                f"Could not fetch a valid futures quote for {symbol}: {exc}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved {instrument.exchange} {symbol} futures quote "
                f"for {snapshot.expiry_date} at {snapshot.timestamp.isoformat()}."
            )
        )
