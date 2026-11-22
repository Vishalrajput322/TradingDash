from datetime import datetime, timezone
from decimal import Decimal

from django.test import TestCase

from analytics.services.max_pain_service import MaxPainService
from analytics.tests.factories import create_snapshot


class MaxPainServiceTest(TestCase):
    def setUp(self):
        self.ts = datetime(2026, 11, 22, 10, 0, tzinfo=timezone.utc)

        snapshots = [
            (Decimal("25000.00"), 10000, 200000),
            (Decimal("25100.00"), 50000, 50000),
            (Decimal("25200.00"), 200000, 10000),
        ]
        for strike, call_oi, put_oi in snapshots:
            create_snapshot(
                symbol="NIFTY",
                strike=strike,
                call_oi=call_oi,
                put_oi=put_oi,
                timestamp=self.ts,
            )

    def test_get_max_pain_returns_strike(self):
        result = MaxPainService.get_max_pain(symbol="NIFTY")
        self.assertIsNotNone(result)
        self.assertIn("max_pain_strike", result)
        self.assertEqual(result["max_pain_strike"], Decimal("25100.00"))