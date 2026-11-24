import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction

from market_data.models import Instrument, OptionExpiry
from market_data.services.providers import (
    get_market_data_provider,
    parse_expiry_date,
)
from options.services.snapshot_service import SnapshotService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch NSE option chain data and store snapshots"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="NIFTY",
            help="Instrument symbol to fetch (default: NIFTY)",
        )
        parser.add_argument(
            "--expiry",
            type=str,
            default=None,
            help="Optional expiry override in DD-MMM-YYYY format (e.g., 26-Nov-2026)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch and validate option chain data without writing to the database",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"].strip().upper()
        requested_expiry = options["expiry"].strip() if options["expiry"] else None
        dry_run = options["dry_run"]

        try:
            instrument = Instrument.objects.get(symbol=symbol, is_active=True)
        except Instrument.DoesNotExist as exc:
            raise CommandError(f"Active Instrument not found for symbol '{symbol}'.") from exc
        except Instrument.MultipleObjectsReturned as exc:
            raise CommandError(f"Multiple active Instrument records found for symbol '{symbol}'.") from exc
        except Exception as exc:
            # Fallback if your Instrument model doesn't define `is_active`
            try:
                instrument = Instrument.objects.get(symbol=symbol)
            except Instrument.DoesNotExist as inner_exc:
                raise CommandError(f"Instrument not found for symbol '{symbol}'.") from inner_exc
            except Exception as db_exc:
                logger.exception("Database error while loading instrument %s", symbol)
                raise CommandError(f"Database error loading instrument '{symbol}': {db_exc}") from db_exc

        try:
            client = get_market_data_provider(instrument.exchange)
        except Exception as exc:
            raise CommandError(
                f"Unable to load {instrument.exchange} market data provider: {exc}"
            ) from exc
        snapshot_service = SnapshotService()

        try:
            if requested_expiry:
                data, expiry_str = client.option_chain(
                    symbol,
                    expiry=requested_expiry,
                    asset_class=instrument.asset_class,
                )
            else:
                data, expiry_str = client.option_chain(
                    symbol,
                    asset_class=instrument.asset_class,
                )
        except Exception as exc:
            logger.exception("Failed to fetch option chain data for %s", symbol)
            raise CommandError(f"Failed to fetch option chain for {symbol}: {exc}") from exc

        if not data or not expiry_str:
            raise CommandError(f"Empty option chain response returned for {symbol} (expiry={expiry_str!r}).")

        try:
            expiry_date = parse_expiry_date(expiry_str)
        except ValueError as exc:
            raise CommandError(f"Unexpected expiry date format '{expiry_str}' for {symbol}.") from exc

        self.stdout.write(
            f"Fetched option chain for {symbol} | expiry={expiry_str} ({expiry_date})"
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Skipping database persistence for {symbol} ({expiry_date}).")
            )
            return

        try:
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
        except DatabaseError as exc:
            logger.exception("Database error while saving option chain snapshot for %s", symbol)
            raise CommandError(f"Database error saving snapshot for {symbol}: {exc}") from exc
        except Exception as exc:
            logger.exception("Error while saving option chain snapshot for %s", symbol)
            raise CommandError(f"Failed saving snapshot for {symbol}: {exc}") from exc

        status_msg = (
            f"Saved snapshot for {symbol} ({expiry_date}, new_expiry={created}): {result}"
        )
        logger.info(status_msg)
        self.stdout.write(self.style.SUCCESS(status_msg))