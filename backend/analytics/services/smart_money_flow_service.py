from decimal import Decimal
from typing import Optional, TypedDict

from analytics.services.max_pain_service import MaxPainService
from analytics.services.oi_buildup_service import (
    OIBuildupService,
    OISignals,
    StrikeBuildup,
)
from analytics.services.pcr_service import PCRService


class SmartMoneyFlowResponse(TypedDict):
    pcr: Optional[float]
    market_bias: str
    max_pain: Optional[Decimal]

    # Call (CE) positioning buckets
    top_call_long_buildup: list[StrikeBuildup]
    top_call_short_buildup: list[StrikeBuildup]
    top_call_short_covering: list[StrikeBuildup]
    top_call_long_unwinding: list[StrikeBuildup]

    # Put (PE) positioning buckets
    top_put_long_buildup: list[StrikeBuildup]
    top_put_short_buildup: list[StrikeBuildup]
    top_put_short_covering: list[StrikeBuildup]
    top_put_long_unwinding: list[StrikeBuildup]


class SmartMoneyFlowService:
    """Aggregates PCR, Max Pain, and separate Call/Put OI buildup buckets."""

    @staticmethod
    def get_smart_money_flow(symbol: str) -> SmartMoneyFlowResponse:
        pcr_data = PCRService.get_latest_pcr(symbol=symbol)
        max_pain_data = MaxPainService.get_max_pain(symbol=symbol)
        buildup_data = OIBuildupService.get_buildup_signals(symbol=symbol)

        pcr: Optional[float] = pcr_data["pcr"] if pcr_data else None

        if pcr is None:
            market_bias = "NEUTRAL"
        elif pcr > 1.2:
            market_bias = "BULLISH"
        elif pcr < 0.8:
            market_bias = "BEARISH"
        else:
            market_bias = "NEUTRAL"

        signals = buildup_data["signals"] if buildup_data else []

        call_long_buildup: list[StrikeBuildup] = []
        call_short_buildup: list[StrikeBuildup] = []
        call_short_covering: list[StrikeBuildup] = []
        call_long_unwinding: list[StrikeBuildup] = []

        put_long_buildup: list[StrikeBuildup] = []
        put_short_buildup: list[StrikeBuildup] = []
        put_short_covering: list[StrikeBuildup] = []
        put_long_unwinding: list[StrikeBuildup] = []

        for signal in signals:
            call_sig = signal["call_signal"]
            put_sig = signal["put_signal"]

            # Classify Call (CE) side
            if call_sig == OISignals.LONG_BUILDUP.value:
                call_long_buildup.append(signal)
            elif call_sig == OISignals.SHORT_BUILDUP.value:
                call_short_buildup.append(signal)
            elif call_sig == OISignals.SHORT_COVERING.value:
                call_short_covering.append(signal)
            elif call_sig == OISignals.LONG_UNWINDING.value:
                call_long_unwinding.append(signal)

            # Classify Put (PE) side
            if put_sig == OISignals.LONG_BUILDUP.value:
                put_long_buildup.append(signal)
            elif put_sig == OISignals.SHORT_BUILDUP.value:
                put_short_buildup.append(signal)
            elif put_sig == OISignals.SHORT_COVERING.value:
                put_short_covering.append(signal)
            elif put_sig == OISignals.LONG_UNWINDING.value:
                put_long_unwinding.append(signal)

        # Rank all buckets by combined Call + Put OI movement
        total_oi_impact = lambda x: abs(x["call_oi_change"]) + abs(x["put_oi_change"])

        for bucket in (
            call_long_buildup,
            call_short_buildup,
            call_short_covering,
            call_long_unwinding,
            put_long_buildup,
            put_short_buildup,
            put_short_covering,
            put_long_unwinding,
        ):
            bucket.sort(key=total_oi_impact, reverse=True)

        return {
            "pcr": pcr,
            "market_bias": market_bias,
            "max_pain": max_pain_data["max_pain_strike"] if max_pain_data else None,
            "top_call_long_buildup": call_long_buildup[:10],
            "top_call_short_buildup": call_short_buildup[:10],
            "top_call_short_covering": call_short_covering[:10],
            "top_call_long_unwinding": call_long_unwinding[:10],
            "top_put_long_buildup": put_long_buildup[:10],
            "top_put_short_buildup": put_short_buildup[:10],
            "top_put_short_covering": put_short_covering[:10],
            "top_put_long_unwinding": put_long_unwinding[:10],
        }