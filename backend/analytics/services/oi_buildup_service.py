from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, TypedDict, Union
import logging

from django.db.models import QuerySet
from options.models import OptionChainSnapshot

logger = logging.getLogger(__name__)


class OISignals(str, Enum):
    LONG_BUILDUP = "LONG_BUILDUP"
    SHORT_BUILDUP = "SHORT_BUILDUP"
    LONG_UNWINDING = "LONG_UNWINDING"
    SHORT_COVERING = "SHORT_COVERING"
    NEUTRAL = "NEUTRAL"


class StrikeBuildup(TypedDict):
    strike: Decimal

    call_price_change: float
    call_oi_change: int
    call_signal: str

    put_price_change: float
    put_oi_change: int
    put_signal: str


class OIBuildupResponse(TypedDict):
    latest_timestamp: str
    previous_timestamp: str
    total_strikes: int
    signals: list[StrikeBuildup]


class OIBuildupService:
    """Service for classifying strike-level Open Interest buildup and unwinding."""

    @staticmethod
    def classify(
        price_change: float,
        oi_change: int,
    ) -> OISignals:
        if price_change > 0 and oi_change > 0:
            return OISignals.LONG_BUILDUP

        if price_change < 0 and oi_change > 0:
            return OISignals.SHORT_BUILDUP

        if price_change < 0 and oi_change < 0:
            return OISignals.LONG_UNWINDING

        if price_change > 0 and oi_change < 0:
            return OISignals.SHORT_COVERING

        return OISignals.NEUTRAL

    @staticmethod
    def get_buildup_signals(
        symbol: str,
        expiry_date: Optional[Union[date, datetime]] = None,
    ) -> OIBuildupResponse | None:
        queryset: QuerySet[OptionChainSnapshot] = OptionChainSnapshot.objects.filter(
            instrument__symbol=symbol
        )

        if expiry_date:
            queryset = queryset.filter(expiry__expiry_date=expiry_date)

        # 1. Get latest two distinct snapshot timestamps
        recent_timestamps = list(
            queryset.values_list("timestamp", flat=True)
            .distinct()
            .order_by("-timestamp")[:2]
        )

        if len(recent_timestamps) < 2:
            logger.warning(
                "Insufficient snapshot history for %s (found %d timestamp(s)).",
                symbol,
                len(recent_timestamps),
            )
            return None

        latest_ts = recent_timestamps[0]
        previous_ts = recent_timestamps[1]

        snapshot_qs = queryset.filter(timestamp__in=[latest_ts, previous_ts])

        # Isolate nearest expiry if expiry_date is not explicitly passed
        if not expiry_date:
            nearest_expiry = (
                snapshot_qs.order_by("expiry__expiry_date")
                .values_list("expiry__expiry_date", flat=True)
                .first()
            )
            if nearest_expiry:
                snapshot_qs = snapshot_qs.filter(expiry__expiry_date=nearest_expiry)

        # 2. Fetch required fields only
        rows = snapshot_qs.values(
            "timestamp",
            "strike",
            "call_ltp",
            "put_ltp",
            "call_oi",
            "put_oi",
        )

        # 3. Build O(1) lookup maps keyed by strike
        latest_map: dict[Decimal, dict] = {}
        previous_map: dict[Decimal, dict] = {}

        for row in rows:
            strike: Decimal = row["strike"]
            data = {
                "call_ltp": row["call_ltp"],
                "put_ltp": row["put_ltp"],
                "call_oi": row["call_oi"],
                "put_oi": row["put_oi"],
            }

            if row["timestamp"] == latest_ts:
                latest_map[strike] = data
            else:
                previous_map[strike] = data

        # 4. Convert maps into classified strike signals
        signals: list[StrikeBuildup] = []
        all_strikes = sorted(set(latest_map.keys()) | set(previous_map.keys()))

        for strike in all_strikes:
            curr = latest_map.get(strike)
            prev = previous_map.get(strike)

            # Guard against strikes missing in either snapshot or NULL DB values
            if not curr or not prev:
                continue

            call_price_change = (curr["call_ltp"] or Decimal("0")) - (
                prev["call_ltp"] or Decimal("0")
            )
            call_oi_change = (curr["call_oi"] or 0) - (prev["call_oi"] or 0)

            put_price_change = (curr["put_ltp"] or Decimal("0")) - (
                prev["put_ltp"] or Decimal("0")
            )
            put_oi_change = (curr["put_oi"] or 0) - (prev["put_oi"] or 0)

            call_price_delta = round(float(call_price_change), 2)
            put_price_delta = round(float(put_price_change), 2)

            call_signal = OIBuildupService.classify(
                call_price_delta,
                call_oi_change,
            )
            put_signal = OIBuildupService.classify(
                put_price_delta,
                put_oi_change,
            )

            signals.append(
                {
                    "strike": strike,
                    "call_price_change": call_price_delta,
                    "call_oi_change": call_oi_change,
                    "call_signal": call_signal.value,
                    "put_price_change": put_price_delta,
                    "put_oi_change": put_oi_change,
                    "put_signal": put_signal.value,
                }
            )

        # 5. Rank by highest total OI movement so most active strikes appear first
        signals.sort(
            key=lambda x: abs(x["call_oi_change"]) + abs(x["put_oi_change"]),
            reverse=True,
        )

        return {
            "latest_timestamp": latest_ts.isoformat(),
            "previous_timestamp": previous_ts.isoformat(),
            "total_strikes": len(signals),
            "signals": signals,
        }