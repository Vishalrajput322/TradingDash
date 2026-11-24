from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from analytics.services.dashboard_service import DashboardService
from market_data.models import Instrument, OptionExpiry
from options.models import OptionChainSnapshot


class DashboardServiceTests(TestCase):
    @patch("analytics.services.dashboard_service.SmartMoneyFlowService.get_smart_money_flow")
    @patch("analytics.services.dashboard_service.OIBuildupService.get_buildup_signals")
    @patch("analytics.services.dashboard_service.MaxPainService.get_max_pain")
    @patch("analytics.services.dashboard_service.PCRService.get_latest_pcr")
    def test_dashboard_handles_snapshot_without_analytics_history(
        self,
        get_pcr,
        get_max_pain,
        get_buildup,
        get_smart_money,
    ):
        instrument, _ = Instrument.objects.get_or_create(
            symbol="NIFTY",
            defaults={"name": "NIFTY"},
        )
        expiry = OptionExpiry.objects.create(
            instrument=instrument,
            expiry_date=date(2027, 1, 5),
        )
        OptionChainSnapshot.objects.create(
            instrument=instrument,
            expiry=expiry,
            strike=Decimal("25000"),
            call_oi=100,
            put_oi=120,
            call_oi_change=0,
            put_oi_change=0,
            call_volume=10,
            put_volume=10,
            call_ltp=Decimal("100"),
            put_ltp=Decimal("100"),
            timestamp=timezone.make_aware(datetime(2026, 11, 24, 9, 0)),
        )
        get_pcr.return_value = None
        get_max_pain.return_value = None
        get_buildup.return_value = None
        get_smart_money.return_value = {}

        payload = DashboardService.get_dashboard("NIFTY", use_cache=False)

        self.assertEqual(payload["market_bias"], "NEUTRAL")
        self.assertIsNone(payload["pcr"])
        self.assertIsNone(payload["max_pain"])
        self.assertEqual(payload["top_call_long_buildup"], [])
