import logging
from typing import List, Optional
from django.utils import timezone

from alerts.models import AlertHistory, AlertSeverity
from alerts.services.alert_rules import (
    BaseAlertRule,
    PCRThresholdRule,
    MaxPainShiftRule,
    LongBuildupRule,
    ShortCoveringRule,
)

logger = logging.getLogger(__name__)


class AlertEngine:
    def __init__(self, rules: Optional[List[BaseAlertRule]] = None, cooldown_minutes: int = 60):
        self.cooldown_minutes = cooldown_minutes
        self.rules = rules or [
            PCRThresholdRule(upper_threshold=1.5, lower_threshold=0.6),
            MaxPainShiftRule(),
            LongBuildupRule(min_oi_change=500000),
            ShortCoveringRule(),
        ]

    def run(self, current_data: dict, previous_data: Optional[dict] = None, persist: bool = True) -> List[dict]:
        """
        Evaluates all registered rules against dashboard data.
        Fault-tolerant per rule, deduplicates via AlertHistory, and attaches evaluation metadata.
        """
        symbol = current_data.get("symbol")
        if not symbol or "error" in current_data:
            return []

        triggered_alerts = []

        for rule in self.rules:
            rule_name = rule.__class__.__name__

            try:
                alert = rule.evaluate(
                    current_data=current_data,
                    previous_data=previous_data,
                )
            except Exception:
                logger.exception("Alert rule failed: %s", rule_name)
                continue

            if not alert:
                continue

            # Ensure rule name, severity, and evaluation timestamp are always populated
            alert.setdefault("rule", rule_name)
            alert.setdefault("severity", AlertSeverity.MEDIUM.value)
            alert["evaluated_at"] = timezone.now().isoformat()

            # Skip if this exact alert type fired recently for this symbol
            if persist and AlertHistory.is_duplicate(symbol, alert["type"], self.cooldown_minutes):
                continue

            if persist:
                AlertHistory.objects.create(
                    alert_type=alert["type"],
                    rule_name=alert["rule"],
                    severity=alert["severity"],
                    symbol=symbol,
                    message=alert["message"],
                    metadata=alert.get("metadata", {}),
                )

            triggered_alerts.append(alert)

        return  triggered_alerts