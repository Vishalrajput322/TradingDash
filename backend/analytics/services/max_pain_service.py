from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TypedDict, Union
import logging

from django.db.models import QuerySet
from options.models import OptionChainSnapshot

logger = logging.getLogger(__name__)


class StrikePainDetail(TypedDict):
    strike: Decimal
    call_pain: Decimal
    put_pain: Decimal
    total_pain: Decimal


class MaxPainResponse(TypedDict):
    symbol: str
    timestamp: str
    max_pain_strike: Decimal
    min_total_pain: Decimal
    total_strikes: int
    pain_distribution: list[StrikePainDetail]


class MaxPainService:
    """Service for computing the Option Max Pain strike from the latest option chain snapshot."""

    @staticmethod
    def get_max_pain(
        symbol: str,
        expiry_date: Optional[Union[date, datetime]] = None,
    ) -> Optional[MaxPainResponse]:
        """
        Calculates the Max Pain strike where option writers (sellers) face the
        minimum cumulative payout at expiration.

        Args:
            symbol: Underlying instrument symbol (e.g., 'NIFTY').
            expiry_date: Optional expiry date filter. Defaults to the nearest active expiry
                         if multiple expiries exist in the latest snapshot.

        Returns:
            Dictionary with max_pain_strike, minimum total pain, and the full strike-wise
            pain curve (useful for plotting Max Pain charts), or None if no data exists.
        """
        queryset: QuerySet[OptionChainSnapshot] = OptionChainSnapshot.objects.filter(
            instrument__symbol=symbol
        )

        if expiry_date:
            queryset = queryset.filter(expiry__expiry_date=expiry_date)

        # 1. Fetch latest snapshot timestamp
        latest_timestamp = (
            queryset.order_by("-timestamp")
            .values_list("timestamp", flat=True)
            .first()
        )

        if not latest_timestamp:
            logger.warning(
                "No OptionChainSnapshot records found for symbol=%s%s.",
                symbol,
                f", expiry={expiry_date}" if expiry_date else "",
            )
            return None

        snapshot_qs = queryset.filter(timestamp=latest_timestamp)

        # Guard: Max Pain is strictly an expiry-specific calculation.
        # If expiry_date wasn't passed and multiple expiries exist in the snapshot,
        # default to the nearest expiry so strikes from different expiries don't mix.
        if not expiry_date:
            nearest_expiry = (
                snapshot_qs.order_by("expiry__expiry_date")
                .values_list("expiry__expiry_date", flat=True)
                .first()
            )
            if nearest_expiry:
                snapshot_qs = snapshot_qs.filter(expiry__expiry_date=nearest_expiry)

        # 2. Fetch lightweight strike rows sorted in ascending order
        rows = list(
            snapshot_qs.values("strike", "call_oi", "put_oi").order_by("strike")
        )

        if not rows:
            logger.warning(
                "Empty strike rows for symbol=%s at timestamp=%s.",
                symbol,
                latest_timestamp,
            )
            return None

        # Normalize rows into clean tuples for fast inner-loop calculation
        chain_data: list[tuple[Decimal, int, int]] = [
            (
                row["strike"],
                row["call_oi"] or 0,
                row["put_oi"] or 0,
            )
            for row in rows
        ]

        # 3. Calculate cumulative writer pain for every candidate expiry strike
        pain_distribution: list[StrikePainDetail] = []

        for candidate_strike, _, _ in chain_data:
            call_pain = Decimal("0")
            put_pain = Decimal("0")

            for strike, call_oi, put_oi in chain_data:
                if strike < candidate_strike and call_oi > 0:
                    # ITM Calls: writers pay (expiry_price - strike) * call_oi
                    call_pain += (candidate_strike - strike) * Decimal(call_oi)
                elif strike > candidate_strike and put_oi > 0:
                    # ITM Puts: writers pay (strike - expiry_price) * put_oi
                    put_pain += (strike - candidate_strike) * Decimal(put_oi)

            total_pain = call_pain + put_pain
            pain_distribution.append(
                {
                    "strike": candidate_strike,
                    "call_pain": call_pain,
                    "put_pain": put_pain,
                    "total_pain": total_pain,
                }
            )
        top_candidates = sorted(pain_distribution,key=lambda x: x["total_pain"])[:5]
        # 4. Identify the strike with the minimum total pain
        min_pain_entry = min(pain_distribution, key=lambda item: item["total_pain"])

        return {
            "symbol": symbol,
            "timestamp": latest_timestamp.isoformat(),
            "max_pain_strike": min_pain_entry["strike"],
            "min_total_pain": min_pain_entry["total_pain"],
            "total_strikes": len(pain_distribution),
            "pain_distribution": pain_distribution,
            "top_candidates": top_candidates
        }