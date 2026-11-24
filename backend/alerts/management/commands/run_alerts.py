from django.core.management.base import BaseCommand
from analytics.services.dashboard_service import DashboardService
from alerts.services.alert_engine import AlertEngine


class Command(BaseCommand):
    help = "Evaluates market alert rules against the latest dashboard data and stores triggered alerts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbols",
            nargs="+",
            type=str,
            default=["NIFTY", "BANKNIFTY"],
            help="Symbols to evaluate (default: NIFTY BANKNIFTY)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Evaluate rules without saving to AlertHistory or checking cooldowns.",
        )

    def handle(self, *args, **options):
        symbols = [s.upper().strip() for s in options["symbols"]]
        dry_run = options["dry_run"]
        engine = AlertEngine()

        total_alerts = 0

        for symbol in symbols:
            # Always bypass cache during alert runs so fresh snapshots aren't missed
            current_data = DashboardService.get_dashboard(symbol=symbol, use_cache=False)

            if "error" in current_data:
                self.stdout.write(
                    self.style.WARNING(f"[{symbol}] Skipped: {current_data['error']}")
                )
                continue

            alerts = engine.run(current_data=current_data, persist=not dry_run)
            total_alerts += len(alerts)

            for alert in alerts:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{alert['severity']}] {alert['message']} ({alert['rule']})"
                    )
                )

        if total_alerts == 0:
            self.stdout.write("Generated 0 alert(s)")
        else:
            mode_tag = " (DRY RUN)" if dry_run else ""
            self.stdout.write(
                self.style.SUCCESS(f"\nGenerated {total_alerts} alert(s){mode_tag}")
            )