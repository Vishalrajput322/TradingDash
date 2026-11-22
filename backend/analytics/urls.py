from django.urls import path

from analytics.views import (
    MaxPainAPIView,
    OIChangeAPIView,
    PCRAPIView,
    SmartMoneyFlowAPIView,
)

app_name = "analytics"

urlpatterns = [
    path("pcr/", PCRAPIView.as_view(), name="pcr"),
    path("oi-change/", OIChangeAPIView.as_view(), name="oi-change"),
    path("max-pain/", MaxPainAPIView.as_view(), name="max-pain"),
    path("smart-money-flow/", SmartMoneyFlowAPIView.as_view(), name="smart-money-flow"),
]