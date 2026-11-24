from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from analytics.services.futures_dashboard_service import FuturesDashboardService
from analytics.views import DashboardOverviewAPIView, DashboardRefreshAPIView
from market_data.models import Instrument
from options.models import FuturesSnapshot


class FuturesDashboardServiceTests(TestCase):
    def test_dashboard_returns_latest_quote_and_change_for_nearest_expiry(self):
        instrument = Instrument.objects.create(
            symbol="GOLD",
            name="Gold",
            exchange=Instrument.Exchange.MCX,
            asset_class=Instrument.AssetClass.COMMODITY,
        )
        expiry = date(2027, 1, 5)
        first_timestamp = timezone.make_aware(datetime(2026, 11, 24, 9, 0))
        latest_timestamp = timezone.make_aware(datetime(2026, 11, 24, 9, 1))
        FuturesSnapshot.objects.create(
            instrument=instrument,
            expiry_date=expiry,
            last_price=Decimal("125000.00"),
            open_interest=100,
            oi_change=10,
            volume=200,
            timestamp=first_timestamp,
        )
        FuturesSnapshot.objects.create(
            instrument=instrument,
            expiry_date=expiry,
            last_price=Decimal("125025.50"),
            open_interest=110,
            oi_change=10,
            volume=240,
            timestamp=latest_timestamp,
        )

        payload = FuturesDashboardService.get_dashboard("GOLD", "MCX")

        self.assertEqual(payload["product"], "FUTURES")
        self.assertEqual(payload["last_price"], 125025.5)
        self.assertEqual(payload["price_change"], 25.5)
        self.assertEqual(payload["expiry_date"], "2027-01-05")

    def test_dashboard_reports_when_quote_data_is_missing(self):
        payload = FuturesDashboardService.get_dashboard("GOLD", "MCX")

        self.assertIn("error", payload)
        self.assertEqual(payload["exchange"], "MCX")


class DashboardOverviewApiTests(TestCase):
    @patch("analytics.views.FuturesDashboardService.get_dashboard")
    def test_routes_mcx_futures_selection_to_futures_service(self, get_dashboard):
        get_dashboard.return_value = {
            "symbol": "GOLD",
            "exchange": "MCX",
            "product": "FUTURES",
        }
        request = APIRequestFactory().get(
            "/api/analytics/dashboard/overview/",
            {"symbol": "gold", "exchange": "mcx", "product": "futures"},
        )

        response = DashboardOverviewAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        get_dashboard.assert_called_once_with(symbol="GOLD", exchange="MCX")


class DashboardRefreshApiTests(TestCase):
    @patch("analytics.views.DashboardService.get_dashboard")
    @patch("analytics.views.fetch_option_chain_snapshot")
    def test_fetches_selected_index_and_returns_fresh_dashboard(
        self,
        fetch_snapshot,
        get_dashboard,
    ):
        instrument, _ = Instrument.objects.get_or_create(
            symbol="FINNIFTY",
            defaults={
                "name": "NIFTY FINANCIAL SERVICES",
                "exchange": Instrument.Exchange.NSE,
                "asset_class": Instrument.AssetClass.INDEX,
            },
        )
        get_dashboard.return_value = {
            "symbol": "FINNIFTY",
            "exchange": "NSE",
            "product": "OPTIONS",
        }
        request = APIRequestFactory().post(
            "/api/analytics/dashboard/refresh/",
            {"symbol": "finnifty"},
            format="json",
        )

        response = DashboardRefreshAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        fetch_snapshot.assert_called_once_with(instrument)
        get_dashboard.assert_called_once_with(
            symbol="FINNIFTY",
            exchange="NSE",
            use_cache=False,
        )

    @patch("analytics.views.fetch_option_chain_snapshot")
    def test_rejects_symbols_not_registered_as_active_nse_indices(self, fetch_snapshot):
        request = APIRequestFactory().post(
            "/api/analytics/dashboard/refresh/",
            {"symbol": "UNKNOWN"},
            format="json",
        )

        response = DashboardRefreshAPIView.as_view()(request)

        self.assertEqual(response.status_code, 404)
        fetch_snapshot.assert_not_called()

    @patch(
        "analytics.views.fetch_option_chain_snapshot",
        side_effect=RuntimeError("NSE unavailable"),
    )
    def test_reports_provider_failure_to_the_frontend(self, fetch_snapshot):
        Instrument.objects.get_or_create(
            symbol="FINNIFTY",
            defaults={
                "name": "NIFTY FINANCIAL SERVICES",
                "exchange": Instrument.Exchange.NSE,
                "asset_class": Instrument.AssetClass.INDEX,
            },
        )
        request = APIRequestFactory().post(
            "/api/analytics/dashboard/refresh/",
            {"symbol": "FINNIFTY"},
            format="json",
        )

        response = DashboardRefreshAPIView.as_view()(request)

        self.assertEqual(response.status_code, 502)
        self.assertIn("NSE unavailable", response.data["detail"])
        fetch_snapshot.assert_called_once()
