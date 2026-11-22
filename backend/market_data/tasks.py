from datetime import datetime
import logging

from celery import shared_task
from django.db import DatabaseError, transaction

from market_data.models import Instrument, OptionExpiry
from market_data.services.nse_service import NSEClient
from options.services.snapshot_service import SnapshotService

logger = logging.getLogger(__name__)

TRANSIENT_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
    DatabaseError,
)


@shared_task
def test_task():
    logger.info("CELERY WORKING")
    return "CELERY WORKING"


@shared_task(
    bind=True,
    autoretry_for=TRANSIENT_EXCEPTIONS,
    retry_backoff=15,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=3,
    acks_late=True,
)
def fetch_option_chain(self, symbol: str = "NIFTY", expiry_str_override: str | None = None):
    """Fetch option chain data for a symbol and persist a snapshot atomically."""
    normalized_symbol = symbol.strip().upper()
    expiry_override = expiry_str_override.strip() if expiry_str_override else None

    try:
        instrument = Instrument.objects.get(symbol=normalized_symbol, is_active=True)
    except Instrument.DoesNotExist:
        logger.error("Active Instrument not found for symbol '%s'", normalized_symbol)
        raise
    except Instrument.MultipleObjectsReturned:
        logger.error("Multiple active Instrument records found for symbol '%s'", normalized_symbol)
        raise
    except Exception:
        # Fallback if Instrument model does not define `is_active`
        instrument = Instrument.objects.get(symbol=normalized_symbol)

    client = NSEClient()
    snapshot_service = SnapshotService()

    if expiry_override:
        try:
            data, expiry_str = client.option_chain(normalized_symbol, expiry=expiry_override)
        except TypeError:
            data, expiry_str = client.option_chain(normalized_symbol)
    else:
        data, expiry_str = client.option_chain(normalized_symbol)

    if not data or not expiry_str:
        msg = f"Empty option chain response for {normalized_symbol} (expiry={expiry_str!r})"
        logger.warning(msg)
        raise ValueError(msg)

    expiry_date = datetime.strptime(expiry_str.strip(), "%d-%b-%Y").date()

    with transaction.atomic():
        expiry, created = OptionExpiry.objects.get_or_create(
            instrument=instrument,
            expiry_date=expiry_date,
        )
        result = snapshot_service.save_option_chain(
            instrument=instrument,
            expiry=expiry,
            raw_data=data,
        )

    logger.info(
        "Saved option chain snapshot for %s (expiry=%s, new_expiry=%s): %s",
        normalized_symbol,
        expiry_date,
        created,
        result,
    )
    return {
        "symbol": normalized_symbol,
        "expiry": str(expiry_date),
        "new_expiry": created,
        "result": result,
    }


@shared_task
def fetch_nifty_option_chain():
    """
    Celery Beat entry point for fetching NIFTY option chain snapshots.
    """

    return fetch_option_chain(
        symbol="NIFTY"
    )