from datetime import date
from decimal import Decimal
from django.db import models
from options.models import OptionChainSnapshot


def _build_required_defaults(model_cls, overrides: dict) -> dict:
    """Populates any non-nullable fields without defaults so .create() never fails."""
    defaults = {}
    for field in model_cls._meta.fields:
        if field.primary_key or field.name in overrides:
            continue
        if field.null or field.has_default() or getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            continue

        if isinstance(field, models.CharField):
            defaults[field.name] = "TEST"
        elif isinstance(field, models.IntegerField):
            defaults[field.name] = 0
        elif isinstance(field, models.DecimalField):
            defaults[field.name] = Decimal("0.00")
        elif isinstance(field, models.FloatField):
            defaults[field.name] = 0.0
        elif isinstance(field, models.BooleanField):
            defaults[field.name] = True
    return defaults


def create_snapshot(**kwargs) -> OptionChainSnapshot:
    """Creates an OptionChainSnapshot and any required related models automatically."""
    symbol = kwargs.pop("symbol", "NIFTY")
    expiry_date = kwargs.pop("expiry_date", date(2026, 11, 26))

    # 1. Resolve Instrument dynamically
    instrument_field = OptionChainSnapshot._meta.get_field("instrument")
    if instrument_field.is_relation:
        InstrumentModel = instrument_field.related_model
        inst_defaults = _build_required_defaults(InstrumentModel, {"symbol": symbol})
        instrument, _ = InstrumentModel.objects.get_or_create(
            symbol=symbol,
            defaults=inst_defaults,
        )
        kwargs["instrument"] = instrument

    # 2. Resolve Expiry dynamically (handles both ForeignKey and direct DateField)
    expiry_field = OptionChainSnapshot._meta.get_field("expiry")
    if expiry_field.is_relation:
        ExpiryModel = expiry_field.related_model
        lookup = {"expiry_date": expiry_date}
        if any(f.name == "instrument" for f in ExpiryModel._meta.fields):
            lookup["instrument"] = kwargs["instrument"]
        exp_defaults = _build_required_defaults(ExpiryModel, lookup)
        expiry, _ = ExpiryModel.objects.get_or_create(
            **lookup,
            defaults=exp_defaults,
        )
        kwargs["expiry"] = expiry
    else:
        kwargs["expiry"] = expiry_date

    # 3. Fill any extra required fields on OptionChainSnapshot (e.g., spot_price, volume, iv)
    snap_defaults = _build_required_defaults(OptionChainSnapshot, kwargs)
    snap_defaults.update(kwargs)

    return OptionChainSnapshot.objects.create(**snap_defaults)