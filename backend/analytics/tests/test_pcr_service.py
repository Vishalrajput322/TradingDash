from datetime import datetime, timezone
from decimal import Decimal

from django.test import TestCase

from analytics.services.pcr_service import PCRService
from analytics.tests.factories import create_snapshot


class PCRServiceTest(TestCase):
    def setUp(self):
        self.ts = datetime(2026, 11, 22, 10, 0, tzinfo=timezone.utc)

        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25000.00"),
            call_oi=100000,
            put_oi=150000,
            timestamp=self.ts,
        )
        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25100.00"),
            call_oi=100000,
            put_oi=184000,
            timestamp=self.ts,
        )

    def test_get_latest_pcr_returns_expected_ratio(self):
        result = PCRService.get_latest_pcr(symbol="NIFTY")
        self.assertIsNotNone(result)
        self.assertIn("pcr", result)
        # Total Put OI (334,000) / Total Call OI (200,000) = 1.67
        self.assertEqual(result["pcr"], 1.67)
        self.assertEqual(result["call_oi"], 200000)
        self.assertEqual(result["put_oi"], 334000)

    def test_get_latest_pcr_empty_symbol_returns_none(self):
        result = PCRService.get_latest_pcr(symbol="UNKNOWN")
        self.assertIsNone(result)