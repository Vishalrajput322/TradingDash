from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.test import TestCase

from analytics.services.oi_change_service import OIChangeService
from analytics.tests.factories import create_snapshot


class OIChangeServiceTest(TestCase):
    def setUp(self):
        ts_prev = datetime(2026, 11, 22, 9, 55, tzinfo=timezone.utc)
        ts_curr = ts_prev + timedelta(minutes=5)

        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25800.00"),
            call_oi=100000,
            put_oi=90000,
            timestamp=ts_prev,
        )
        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25800.00"),
            call_oi=115000,
            put_oi=87000,
            timestamp=ts_curr,
        )

    def test_get_oi_change_returns_changes(self):
        result = OIChangeService.get_oi_change(symbol="NIFTY")
        self.assertIsNotNone(result)
        self.assertIn("changes", result)
        self.assertEqual(len(result["changes"]), 1)
        self.assertEqual(result["changes"][0]["call_oi_change"], 15000)
        self.assertEqual(result["changes"][0]["put_oi_change"], -3000)