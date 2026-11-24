from datetime import datetime
from typing import Optional

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.services.max_pain_service import MaxPainService
from analytics.services.oi_change_service import OIChangeService
from analytics.services.pcr_service import PCRService
from analytics.services.smart_money_flow_service import SmartMoneyFlowService

from rest_framework import status
from analytics.services.dashboard_service import DashboardService

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

        symbol = request.query_params.get(
            "symbol",
            "NIFTY"
        )

        data = DashboardService.get_dashboard(
            symbol=symbol
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