from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict, Optional
import logging

from django.db.models import Sum
from django.db.models.functions import Coalesce
from options.models import OptionChainSnapshot

logger = logging.getLogger(__name__)


class PCRResult(TypedDict):
    timestamp: str
    call_oi: int
    put_oi: int
    pcr: Optional[float]


class PCRService:
    """Service for calculating the Put-Call Ratio (PCR) from option chain snapshots."""

    @staticmethod
    def get_latest_pcr(symbol: Optional[str] = None) -> Optional[PCRResult]:
        """
        Calculates the latest Put-Call Ratio based on the most recent snapshot timestamp.
        
        Args:
            symbol: Optional ticker symbol to filter snapshots (recommended for multi-symbol tables).
            
        Returns:
            A dictionary containing timestamp, total call OI, total put OI, and PCR,
            or None if no snapshot data exists.
        """
        queryset = OptionChainSnapshot.objects.all()
        if symbol:
            queryset = queryset.filter(instrument__symbol=symbol)

        # Fetch only the timestamp column to minimize memory and I/O overhead
        latest_timestamp = (
            queryset.order_by("-timestamp")
            .values_list("timestamp", flat=True)
            .first()
        )

        if not latest_timestamp:
            logger.warning("No OptionChainSnapshot records found%s.", f" for {symbol}" if symbol else "")
            return None

        # Coalesce ensures DB returns 0 instead of None if all rows have NULL OI
        totals = queryset.filter(timestamp=latest_timestamp).aggregate(
            total_call_oi=Coalesce(Sum("call_oi"), 0),
            total_put_oi=Coalesce(Sum("put_oi"), 0),
        )

        call_oi: int = totals["total_call_oi"]
        put_oi: int = totals["total_put_oi"]

        if call_oi <= 0:
            logger.warning(
                "Call OI is %s at timestamp %s%s; cannot compute valid PCR.",
                call_oi,
                latest_timestamp,
                f" for {symbol}" if symbol else "",
            )
            pcr = None
        else:
            # Use Decimal for accurate financial rounding rather than float's round()
            raw_pcr = Decimal(put_oi) / Decimal(call_oi)
            pcr = float(raw_pcr.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        return {
            "timestamp": latest_timestamp.isoformat(),
            "call_oi": call_oi,
            "put_oi": put_oi,
            "pcr": pcr,
        }