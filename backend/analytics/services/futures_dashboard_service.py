from django.utils import timezone

from options.models import FuturesSnapshot


class FuturesDashboardService:
    @staticmethod
    def get_dashboard(symbol: str, exchange: str, expiry_date=None) -> dict:
        queryset = FuturesSnapshot.objects.filter(
            instrument__symbol=symbol,
            instrument__exchange=exchange,
        )
        if expiry_date:
            queryset = queryset.filter(expiry_date=expiry_date)
        else:
            nearest_expiry = (
                queryset.filter(expiry_date__gte=timezone.localdate())
                .order_by("expiry_date")
                .values_list("expiry_date", flat=True)
                .first()
            )
            if nearest_expiry:
                queryset = queryset.filter(expiry_date=nearest_expiry)

        latest = queryset.order_by("-timestamp").first()
        if not latest:
            return {
                "error": f"No {exchange} futures snapshots found for '{symbol}'.",
                "symbol": symbol,
                "exchange": exchange,
                "product": "FUTURES",
            }

        previous = queryset.filter(
            timestamp__lt=latest.timestamp,
        ).order_by("-timestamp").first()
        price_change = (
            float(latest.last_price - previous.last_price) if previous else None
        )

        return {
            "symbol": symbol,
            "exchange": exchange,
            "product": "FUTURES",
            "last_price": float(latest.last_price),
            "price_change": price_change,
            "open_interest": latest.open_interest,
            "oi_change": latest.oi_change,
            "volume": latest.volume,
            "expiry_date": latest.expiry_date.isoformat(),
            "snapshot_timestamp": latest.timestamp.isoformat(),
        }
