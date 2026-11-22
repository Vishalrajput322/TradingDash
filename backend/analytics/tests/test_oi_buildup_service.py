from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from analytics.services.oi_buildup_service import OIBuildupService, OISignals
from analytics.tests.factories import create_snapshot


class OIBuildupClassifyTest(SimpleTestCase):
    """Pure unit tests for buildup classification without touching the database."""

    def test_long_buildup(self):
        self.assertEqual(OIBuildupService.classify(10.0, 100), OISignals.LONG_BUILDUP)

    def test_short_buildup(self):
        self.assertEqual(OIBuildupService.classify(-10.0, 100), OISignals.SHORT_BUILDUP)

    def test_long_unwinding(self):
        self.assertEqual(OIBuildupService.classify(-10.0, -100), OISignals.LONG_UNWINDING)

    def test_short_covering(self):
        self.assertEqual(OIBuildupService.classify(10.0, -100), OISignals.SHORT_COVERING)

    def test_neutral_when_no_change(self):
        self.assertEqual(OIBuildupService.classify(0.0, 0), OISignals.NEUTRAL)


class OIBuildupServiceDBTest(TestCase):
    def setUp(self):
        ts_prev = datetime(2026, 11, 22, 9, 55, tzinfo=timezone.utc)
        ts_curr = ts_prev + timedelta(minutes=5)

        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25800.00"),
            call_ltp=Decimal("120.00"),
            put_ltp=Decimal("110.00"),
            call_oi=100000,
            put_oi=100000,
            timestamp=ts_prev,
        )
        create_snapshot(
            symbol="NIFTY",
            strike=Decimal("25800.00"),
            call_ltp=Decimal("135.00"),  # Price ↑ + OI ↑ -> LONG_BUILDUP
            put_ltp=Decimal("95.00"),    # Price ↓ + OI ↑ -> SHORT_BUILDUP
            call_oi=125000,
            put_oi=130000,
            timestamp=ts_curr,
        )

    def test_get_buildup_signals_classifies_both_sides(self):
        result = OIBuildupService.get_buildup_signals(symbol="NIFTY")
        self.assertIsNotNone(result)
        self.assertEqual(result["total_strikes"], 1)
        signal = result["signals"][0]
        self.assertEqual(signal["call_signal"], OISignals.LONG_BUILDUP.value)
        self.assertEqual(signal["put_signal"], OISignals.SHORT_BUILDUP.value)