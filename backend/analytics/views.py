import logging
from datetime import datetime
from typing import Optional

from django.core.cache import cache
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.services.max_pain_service import MaxPainService
from analytics.services.oi_change_service import OIChangeService
from analytics.services.pcr_service import PCRService
from analytics.services.smart_money_flow_service import SmartMoneyFlowService
from analytics.services.dashboard_service import DashboardService
from analytics.services.futures_dashboard_service import FuturesDashboardService
from market_data.models import Instrument
from market_data.services.option_chain_service import fetch_option_chain_snapshot

logger = logging.getLogger(__name__)

def _parse_symbol(request: Request) -> str:
    return request.query_params.get("symbol", "NIFTY").strip().upper()


def _parse_expiry_date(request: Request) -> Optional[datetime.date]:
    raw_date = request.query_params.get("expiry_date")
    if not raw_date:
        return None
    return datetime.strptime(raw_date.strip(), "%Y-%m-%d").date()


class PCRAPIView(APIView):
    """GET /api/analytics/pcr/?symbol=NIFTY"""

    def get(self, request: Request) -> Response:
        symbol = _parse_symbol(request)
        result = PCRService.get_latest_pcr(symbol=symbol)

        if result is None:
            return Response(
                {"detail": f"No PCR snapshot data found for symbol '{symbol}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class OIChangeAPIView(APIView):
    """GET /api/analytics/oi-change/?symbol=NIFTY&expiry_date=2026-11-26"""

    def get(self, request: Request) -> Response:
        symbol = _parse_symbol(request)
        try:
            expiry_date = _parse_expiry_date(request)
        except ValueError:
            return Response(
                {"detail": "Invalid expiry_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = OIChangeService.get_oi_change(
            symbol=symbol,
            expiry_date=expiry_date,
        )

        if result is None:
            return Response(
                {"detail": f"Insufficient snapshot data to compute OI change for '{symbol}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class MaxPainAPIView(APIView):
    """GET /api/analytics/max-pain/?symbol=NIFTY&expiry_date=2026-11-26"""

    def get(self, request: Request) -> Response:
        symbol = _parse_symbol(request)
        try:
            expiry_date = _parse_expiry_date(request)
        except ValueError:
            return Response(
                {"detail": "Invalid expiry_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = MaxPainService.get_max_pain(
            symbol=symbol,
            expiry_date=expiry_date,
        )

        if result is None:
            return Response(
                {"detail": f"No Max Pain snapshot data found for symbol '{symbol}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class SmartMoneyFlowAPIView(APIView):
    """GET /api/analytics/smart-money-flow/?symbol=NIFTY"""

    def get(self, request: Request) -> Response:
        symbol = _parse_symbol(request)
        result = SmartMoneyFlowService.get_smart_money_flow(symbol=symbol)

        if result is None:
            return Response(
                {"detail": f"No Smart Money Flow data found for symbol '{symbol}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class DashboardOverviewAPIView(APIView):

    def get(self, request):
        symbol = _parse_symbol(request)
        exchange = request.query_params.get("exchange", "NSE").strip().upper()
        product = request.query_params.get("product", "OPTIONS").strip().upper()
        if exchange not in ("NSE", "MCX"):
            return Response(
                {"detail": "Unsupported exchange. Use NSE or MCX."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if product == "OPTIONS":
            data = DashboardService.get_dashboard(
                symbol=symbol,
                exchange=exchange,
            )
        elif product == "FUTURES":
            data = FuturesDashboardService.get_dashboard(
                symbol=symbol,
                exchange=exchange,
            )
        else:
            return Response(
                {"detail": "Unsupported product. Use OPTIONS or FUTURES."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "error" in data:
            return Response(
                data,
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data,
            status=status.HTTP_200_OK
        )


class DashboardRefreshAPIView(APIView):
    def post(self, request: Request) -> Response:
        if not isinstance(request.data, dict):
            return Response(
                {"detail": "A valid symbol is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        symbol = request.data.get("symbol", "")
        if not isinstance(symbol, str) or not symbol.strip():
            return Response(
                {"detail": "A valid symbol is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        symbol = symbol.strip().upper()

        try:
            instrument = Instrument.objects.get(
                symbol=symbol,
                exchange=Instrument.Exchange.NSE,
                asset_class=Instrument.AssetClass.INDEX,
                is_active=True,
            )
        except Instrument.DoesNotExist:
            return Response(
                {"detail": f"No active NSE index instrument found for '{symbol}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            fetch_option_chain_snapshot(instrument)
        except (RuntimeError, ValueError) as exc:
            logger.exception("Failed to refresh option chain for %s", symbol)
            return Response(
                {"detail": f"Unable to fetch option-chain data for '{symbol}': {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.delete(f"dashboard_overview:NSE:{symbol}")
        data = DashboardService.get_dashboard(
            symbol=symbol,
            exchange=Instrument.Exchange.NSE,
            use_cache=False,
        )
        if "error" in data:
            return Response(data, status=status.HTTP_502_BAD_GATEWAY)

        return Response(data, status=status.HTTP_200_OK)