from django.core.cache import cache
from django.utils import timezone

# Adjust these imports to match your exact file structure
from options.models import OptionChainSnapshot
from analytics.services.pcr_service import PCRService
from analytics.services.max_pain_service import MaxPainService
from analytics.services.oi_buildup_service import OIBuildupService
from analytics.services.smart_money_flow_service import SmartMoneyFlowService


class DashboardService:
    CACHE_TTL = 60  # Cache dashboard payload for 60 seconds

    @classmethod
    def get_dashboard(
        cls,
        symbol: str,
        exchange: str = "NSE",
        use_cache: bool = True,
    ) -> dict:
        symbol = symbol.upper().strip()
        exchange = exchange.upper().strip()
        cache_key = f"dashboard_overview:{exchange}:{symbol}"

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        # 1. Fetch the latest snapshot once to avoid redundant DB queries
        latest_snapshot = (
            OptionChainSnapshot.objects.filter(
                instrument__symbol=symbol,
                instrument__exchange=exchange,
            )
            .order_by("-timestamp")
            .first()
        )

        if not latest_snapshot:
            return {
                "symbol": symbol,
                "exchange": exchange,
                "product": "OPTIONS",
                "error": "No snapshot data available for this symbol.",
                "snapshot_timestamp": None,
            }

        # 2. Aggregate results from your existing services
        # Note: Update method names/arguments if your services accept a snapshot object instead of symbol
        pcr_data = PCRService.get_latest_pcr(symbol=symbol)
        max_pain_data = MaxPainService.get_max_pain(symbol=symbol)
        buildup_data = (OIBuildupService.get_buildup_signals( symbol=symbol))
        smart_money_data = (SmartMoneyFlowService.get_smart_money_flow(symbol=symbol))
        pcr_value = pcr_data.get("pcr") if pcr_data else None
        max_pain = max_pain_data.get("max_pain_strike") if max_pain_data else None

        payload = {
            "symbol": symbol,
            "exchange": exchange,
            "product": "OPTIONS",
            "snapshot_timestamp": latest_snapshot.timestamp.isoformat(),
            "generated_at": timezone.now().isoformat(),
            "pcr": pcr_value,
            "market_bias": cls._derive_market_bias(pcr_value),
            "max_pain": max_pain,
            "top_call_long_buildup": (
                buildup_data.get("top_call_long_buildup", [])[:5]
                if buildup_data
                else []
            ),
            "top_put_long_buildup": (
                buildup_data.get("top_put_long_buildup", [])[:5]
                if buildup_data
                else []
            ),
            "smart_money_flow": smart_money_data,
        }

        if use_cache:
            cache.set(cache_key, payload, timeout=cls.CACHE_TTL)

        return payload

    @staticmethod
    def _derive_market_bias(pcr: float | None) -> str:
        if pcr is None:
            return "NEUTRAL"
        if pcr >= 1.3:
            return "BULLISH"
        elif pcr <= 0.7:
            return "BEARISH"
        return "NEUTRAL"