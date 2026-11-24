from datetime import timedelta
from enum import Enum
from django.db import models
from django.utils import timezone


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class AlertHistory(models.Model):
    alert_type = models.CharField(max_length=50, db_index=True)
    rule_name = models.CharField(max_length=100, db_index=True, default="UnknownRule")
    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices(),
        default=AlertSeverity.MEDIUM.value,
        db_index=True,
    )
    symbol = models.CharField(max_length=20, db_index=True)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Alert Histories"

    def __str__(self):
        return f"[{self.severity}] [{self.symbol}] {self.alert_type} ({self.rule_name})"

    @classmethod
    def is_duplicate(cls, symbol: str, alert_type: str, cooldown_minutes: int = 60) -> bool:
        """Checks if the same alert was already triggered recently."""
        cutoff = timezone.now() - timedelta(minutes=cooldown_minutes)
        return cls.objects.filter(
            symbol=symbol.upper(),
            alert_type=alert_type,
            created_at__gte=cutoff,
        ).exists()