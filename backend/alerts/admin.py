from django.contrib import admin
from .models import AlertHistory


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = ["symbol", "alert_type", "severity", "rule_name", "created_at"]
    list_filter = ["severity", "alert_type", "created_at"]
    search_fields = ["symbol", "rule_name", "message"]
