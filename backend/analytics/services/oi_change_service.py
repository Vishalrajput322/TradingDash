from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TypedDict, Union
import logging

from django.db.models import QuerySet
from options.models import OptionChainSnapshot

logger = logging.getLogger(__name__)


class StrikeOIChange(TypedDict):
    strike: Decimal
    call_oi: int
    put_oi: int
    call_oi_change: int
    put_oi_change: int


class OIChangeResponse(TypedDict):
    symbol: str
    latest_timestamp: str
    previous_timestamp: str
    total_strikes: int
    changes: list[StrikeOIChange]

class OIChangeService:
    """Service for computing strike-wise Open Interest (OI) changes between consecutive snapshots."""

    @staticmethod
    def get_oi_change(
        symbol: Optional[str] = None,
        expiry_date: Optional[Union[date, datetime]] = None,
    ) -> Optional[OIChangeResponse]:
        """
        Compares the latest snapshot against the immediately preceding snapshot
        to calculate strike-by-strike Call and Put OI changes, ordered by activity impact.

        Args:
            symbol: Optional underlying symbol filter (e.g., 'NIFTY').
            expiry_date: Optional expiry date filter if multiple expiries are stored.

        Returns:
            Dictionary containing timestamps, total strike count, and a list of strike
            OI changes sorted by highest absolute OI change, or None if fewer than 2 snapshots exist.
        """
        queryset: QuerySet[OptionChainSnapshot] = OptionChainSnapshot.objects.all()

        if symbol:
            queryset = queryset.filter(instrument__symbol=symbol)
        if expiry_date:
            queryset = queryset.filter(expiry__expiry_date=expiry_date)

        # 1. Fetch only the two most recent distinct timestamps (LIMIT 2 in SQL)
        recent_timestamps = list(
            queryset.values_list("timestamp", flat=True)
            .distinct()
            .order_by("-timestamp")[:2]
        )

        if len(recent_timestamps) < 2:
            logger.warning(
                "Insufficient snapshot history to compute OI change (found %d timestamp(s)%s).",
                len(recent_timestamps),
                f" for {symbol}" if symbol else "",
            )
            return None

        latest_ts, previous_ts = recent_timestamps[0], recent_timestamps[1]

        # 2. Fetch lightweight dictionaries ordered by strike for clean inspection/debugging
        rows = (
    queryset.filter(
        timestamp__in=[latest_ts, previous_ts]
    )
    .values(
        "timestamp",
        "strike",
        "call_oi",
        "put_oi",
    )
)

        # 3. Build O(1) lookup maps keyed by strike
        latest_map: dict[Decimal, dict] = {}
        previous_map: dict[Decimal, dict] = {}

        for row in rows:
            strike: Decimal = row["strike"]
            if row["timestamp"] == latest_ts:
                latest_map[strike] = row
            else:
                previous_map[strike] = row

        # 4. Compute union of all strikes (handles newly opened or closed strikes safely)
        all_strikes = set(latest_map.keys()) | set(previous_map.keys())

        changes: list[StrikeOIChange] = []
        for strike in all_strikes:
            curr = latest_map.get(strike)
            prev = previous_map.get(strike)

            curr_call_oi = (curr["call_oi"] or 0) if curr else 0
            curr_put_oi = (curr["put_oi"] or 0) if curr else 0

            prev_call_oi = (prev["call_oi"] or 0) if prev else 0
            prev_put_oi = (prev["put_oi"] or 0) if prev else 0

            changes.append(
                {
                    "strike": strike,
                    "call_oi": curr_call_oi,
                    "put_oi": curr_put_oi,
                    "call_oi_change": curr_call_oi - prev_call_oi,
                    "put_oi_change": curr_put_oi - prev_put_oi,
                }
            )

        # 5. Sort by total absolute OI movement so the most active strikes surface first
        changes.sort(
            key=lambda x: abs(x["call_oi_change"]) + abs(x["put_oi_change"]),
            reverse=True,
        )

        return {
    "symbol": symbol,
    "latest_timestamp": latest_ts.isoformat(),
    "previous_timestamp": previous_ts.isoformat(),
    "total_strikes": len(changes),
    "changes": changes,
}