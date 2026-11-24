from abc import ABC, abstractmethod
from typing import Optional
from alerts.models import AlertSeverity


class BaseAlertRule(ABC):
    alert_type: str = "BASE_ALERT"
    default_severity: AlertSeverity = AlertSeverity.MEDIUM

    def _build_alert(
        self,
        symbol: str,
        message: str,
        severity: Optional[AlertSeverity] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        return {
            "type": self.alert_type,
            "rule": self.__class__.__name__,
            "severity": (severity or self.default_severity).value,
            "symbol": symbol,
            "message": message,
            "metadata": metadata or {},
        }

    @abstractmethod
    def evaluate(self, current_data: dict, previous_data: Optional[dict] = None) -> Optional[dict]:
        pass


class PCRThresholdRule(BaseAlertRule):
    alert_type = "PCR_ALERT"
    default_severity = AlertSeverity.HIGH

    def __init__(self, upper_threshold: float = 1.5, lower_threshold: float = 0.6):
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold

    def evaluate(self, current_data: dict, previous_data: Optional[dict] = None) -> Optional[dict]:
        pcr = current_data.get("pcr")
        symbol = current_data.get("symbol")

        if pcr is None:
            return None

        if pcr > self.upper_threshold:
            # Escalate to CRITICAL if PCR is extreme
            severity = AlertSeverity.CRITICAL if pcr >= 1.8 else AlertSeverity.HIGH
            return self._build_alert(
                symbol=symbol,
                message=f"{symbol} PCR crossed above {self.upper_threshold} (Current: {pcr})",
                severity=severity,
                metadata={"pcr": pcr, "threshold": self.upper_threshold},
            )

        if pcr < self.lower_threshold:
            severity = AlertSeverity.CRITICAL if pcr <= 0.45 else AlertSeverity.HIGH
            return self._build_alert(
                symbol=symbol,
                message=f"{symbol} PCR dropped below {self.lower_threshold} (Current: {pcr})",
                severity=severity,
                metadata={"pcr": pcr, "threshold": self.lower_threshold},
            )

        return None


class MaxPainShiftRule(BaseAlertRule):
    alert_type = "MAX_PAIN_SHIFT"
    default_severity = AlertSeverity.MEDIUM

    def evaluate(self, current_data: dict, previous_data: Optional[dict] = None) -> Optional[dict]:
        if not previous_data:
            return None

        curr_mp = current_data.get("max_pain")
        prev_mp = previous_data.get("max_pain")
        symbol = current_data.get("symbol")

        if curr_mp and prev_mp and curr_mp != prev_mp:
            direction = "UP" if curr_mp > prev_mp else "DOWN"
            return self._build_alert(
                symbol=symbol,
                message=f"{symbol} Max Pain shifted {direction} from {prev_mp} to {curr_mp}",
                metadata={"previous": prev_mp, "current": curr_mp},
            )
        return None


class LongBuildupRule(BaseAlertRule):
    alert_type = "LONG_BUILDUP_ALERT"
    default_severity = AlertSeverity.MEDIUM

    def __init__(self, min_oi_change: int = 500000):
        self.min_oi_change = min_oi_change

    def evaluate(self, current_data: dict, previous_data: Optional[dict] = None) -> Optional[dict]:
        symbol = current_data.get("symbol")
        top_puts = current_data.get("top_put_long_buildup", [])

        for strike_info in top_puts:
            oi_change = strike_info.get("oi_change", 0)
            strike = strike_info.get("strike_price")
            if oi_change >= self.min_oi_change:
                return self._build_alert(
                    symbol=symbol,
                    message=f"Heavy Put Long Buildup on {symbol} {strike} PE (+{oi_change:,} OI)",
                    metadata=strike_info,
                )
        return None


class ShortCoveringRule(BaseAlertRule):
    alert_type = "SHORT_COVERING_ALERT"
    default_severity = AlertSeverity.HIGH

    def evaluate(self, current_data: dict, previous_data: Optional[dict] = None) -> Optional[dict]:
        symbol = current_data.get("symbol")
        smart_money = current_data.get("smart_money_flow", {})

        if smart_money.get("signal") == "SHORT_COVERING":
            return self._build_alert(
                symbol=symbol,
                message=f"Strong Short Covering detected in {symbol}",
                metadata=smart_money,
            )
        return None