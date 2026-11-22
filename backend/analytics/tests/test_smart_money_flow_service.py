from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.test import TestCase

from analytics.services.smart_money_flow_service import SmartMoneyFlowService
from analytics.tests.factories import create_snapshot


class SmartMoneyFlowServiceTest(TestCase):
    def setUp(self):
        ts_prev = datetime(2026, 11, 22, 9, 55, tzinfo=timezone.utc)
        ts_curr = ts_prev + timedelta(minutes=5)

        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25500.00"),
            call_ltp=Decimal("150.00"),
            put_ltp=Decimal("100.00"),
            call_oi=100000,
            put_oi=150000,
            timestamp=ts_prev,
        )
        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25500.00"),
            call_ltp=Decimal("165.00"),
            put_ltp=Decimal("88.00"),
            call_oi=120000,
            put_oi=180000,  # PCR = 180k / 120k = 1.50 -> BULLISH
            timestamp=ts_curr,
        )

    def test_get_smart_money_flow_returns_market_bias(self):
        result = SmartMoneyFlowService.get_smart_money_flow(symbol="NIFTY")
        self.assertIsNotNone(result)
        self.assertIn("market_bias", result)
        self.assertEqual(result["market_bias"], "BULLISH")
        self.assertEqual(result["max_pain"], Decimal("25500.00"))
        self.assertEqual(len(result["top_call_long_buildup"]), 1)
        self.assertEqual(len(result["top_put_short_buildup"]), 1)