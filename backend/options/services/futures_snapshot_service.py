from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from django.utils import timezone

from market_data.models import Instrument
from options.models import FuturesSnapshot


class FuturesSnapshotService:
    @staticmethod
    def save_quote(instrument: Instrument, quote: dict[str, Any]) -> FuturesSnapshot:
        try:
            expiry_date = date.fromisoformat(str(quote["expiry_date"]))
            last_price = Decimal(str(quote["last_price"]))
            open_interest = int(quote.get("open_interest", 0))
            oi_change = int(quote.get("oi_change", 0))
            volume = int(quote.get("volume", 0))
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise ValueError(
                "Futures quote must include a valid expiry_date and last_price; "
                "open_interest, oi_change, and volume must be integers."
            ) from exc

        raw_timestamp = quote.get("timestamp")
        if raw_timestamp is None:
            timestamp = timezone.now()
        elif isinstance(raw_timestamp, datetime):
            timestamp = raw_timestamp
        else:
            try:
                timestamp = datetime.fromisoformat(str(raw_timestamp))
            except ValueError as exc:
                raise ValueError("Futures quote timestamp must be ISO-8601.") from exc
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)

        if not last_price.is_finite() or last_price < 0:
            raise ValueError("Futures last_price must be a finite non-negative value.")
        if min(open_interest, volume) < 0:
            raise ValueError("Futures open interest and volume cannot be negative.")

        return FuturesSnapshot.objects.create(
            instrument=instrument,
            expiry_date=expiry_date,
            last_price=last_price,
            open_interest=open_interest,
            oi_change=oi_change,
            volume=volume,
            timestamp=timestamp,
        )
