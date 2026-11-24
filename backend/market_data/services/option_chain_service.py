import logging

from django.db import transaction

from market_data.models import Instrument, OptionExpiry
from market_data.services.providers import (
    get_market_data_provider,
    parse_expiry_date,
)
from options.services.snapshot_service import SnapshotService

logger = logging.getLogger(__name__)


def fetch_option_chain_snapshot(
    instrument: Instrument,
    expiry_override: str | None = None,
) -> dict:
    provider = get_market_data_provider(instrument.exchange)
    data, expiry_str = provider.option_chain(
        instrument.symbol,
        expiry=expiry_override,
        asset_class=instrument.asset_class,
    )

    if not data or not expiry_str:
        raise ValueError(
            f"Empty option chain response for {instrument.symbol} "
            f"(expiry={expiry_str!r})"
        )

    expiry_date = parse_expiry_date(expiry_str)

    with transaction.atomic():
        expiry, created = OptionExpiry.objects.get_or_create(
            instrument=instrument,
            expiry_date=expiry_date,
        )
        result = SnapshotService().save_option_chain(
            instrument=instrument,
            expiry=expiry,
            raw_data=data,
        )

    logger.info(
        "Saved option chain snapshot for %s (expiry=%s, new_expiry=%s): %s",
        instrument.symbol,
        expiry_date,
        created,
        result,
    )
    return {
        "symbol": instrument.symbol,
        "expiry": str(expiry_date),
        "new_expiry": created,
        "result": result,
    }
