from django.test import TestCase
from alerts.models import AlertHistory
from alerts.services.alert_engine import AlertEngine


class AlertEngineTests(TestCase):
    def test_pcr_alert_triggers_and_deduplicates(self):
        engine = AlertEngine(cooldown_minutes=60)
        sample_dashboard = {
            "symbol": "NIFTY",
            "pcr": 1.67,
            "max_pain": 25500,
        }

        # First run should trigger and save
        alerts = engine.run(current_data=sample_dashboard)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["type"], "PCR_ALERT")
        self.assertEqual(AlertHistory.objects.count(), 1)

        # Immediate second run should be suppressed by cooldown
        duplicate_alerts = engine.run(current_data=sample_dashboard)
        self.assertEqual(len(duplicate_alerts), 0)
        self.assertEqual(AlertHistory.objects.count(), 1)