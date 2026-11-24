import logging
from typing import List, Optional
from celery import shared_task

from analytics.services.dashboard_service import DashboardService
from alerts.services.alert_engine import AlertEngine

logger = logging.getLogger(__name__)

DEFAULT_TRACKED_SYMBOLS = ["NIFTY", "BANKNIFTY"]


@shared_task(name="alerts.tasks.process_alerts")
def process_alerts(symbols: Optional[List[str]] = None) -> dict:
    """
    Periodic task to evaluate alert rules across tracked symbols
    and persist deduplicated alerts to AlertHistory.
    """
    target_symbols = symbols or DEFAULT_TRACKED_SYMBOLS
    engine = AlertEngine()
    summary = {
        "evaluated_symbols": [],
        "alerts_generated": 0,
        "alerts": [],
    }

    for symbol in target_symbols:
        symbol = symbol.upper().strip()
        try:
            # Refresh dashboard data directly from DB and update cache
            current_data = DashboardService.get_dashboard(symbol=symbol, use_cache=False)

            if "error" in current_data:
                logger.warning("Skipping alerts for %s: %s", symbol, current_data["error"])
                continue

            triggered = engine.run(current_data=current_data, persist=True)
            summary["evaluated_symbols"].append(symbol)
            summary["alerts_generated"] += len(triggered)
            summary["alerts"].extend(triggered)

            for alert in triggered:
                logger.info(
                    "Alert triggered [%s][%s]: %s",
                    symbol,
                    alert["severity"],
                    alert["message"],
                )

        except Exception:
            logger.exception("Failed processing alerts for symbol: %s", symbol)

    return summary