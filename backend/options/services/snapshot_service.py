from django.db import transaction
from django.utils import timezone

from options.models import OptionChainSnapshot


class SnapshotService:
    """
    Responsible for storing option-chain snapshots.

    Input:
        NSE raw JSON

    Output:
        Stored OptionChainSnapshot records
    """

    def save_option_chain(
        self,
        instrument,
        expiry,
        raw_data: dict,
    ) -> dict:

        records = (
            raw_data
            .get("records", {})
            .get("data", [])
        )

        if not records:
            raise ValueError(
                "No option chain data found in NSE response"
            )

        snapshot_time = timezone.now()

        snapshots = []

        for row in records:

            ce = row.get("CE")
            pe = row.get("PE")

            # Ignore incomplete strikes
            if not ce or not pe:
                continue

            try:

                snapshot = OptionChainSnapshot(
                    instrument=instrument,
                    expiry=expiry,

                    strike=row["strikePrice"],

                    call_oi=ce.get(
                        "openInterest",
                        0,
                    ),
                    put_oi=pe.get(
                        "openInterest",
                        0,
                    ),

                    call_oi_change=ce.get(
                        "changeinOpenInterest",
                        0,
                    ),
                    put_oi_change=pe.get(
                        "changeinOpenInterest",
                        0,
                    ),

                    call_volume=ce.get(
                        "totalTradedVolume",
                        0,
                    ),
                    put_volume=pe.get(
                        "totalTradedVolume",
                        0,
                    ),

                    call_ltp=ce.get(
                        "lastPrice",
                        0,
                    ),
                    put_ltp=pe.get(
                        "lastPrice",
                        0,
                    ),

                    timestamp=snapshot_time,
                )

                snapshots.append(snapshot)

            except Exception as exc:
                print(
                    f"Skipping strike "
                    f"{row.get('strikePrice')} "
                    f"because: {exc}"
                )

        if not snapshots:
            raise ValueError(
                "No valid snapshots generated"
            )

        with transaction.atomic():

            OptionChainSnapshot.objects.bulk_create(
                snapshots,
                batch_size=1000,
            )

        return {
            "instrument": instrument.symbol,
            "expiry": expiry.expiry_date,
            "snapshot_count": len(snapshots),
            "timestamp": snapshot_time,
        }