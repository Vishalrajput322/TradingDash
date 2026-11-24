from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Custom user model to allow easy extension of auth fields.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    Stores trader preferences and alert notification channels.
    """
    class ExchangeChoice(models.TextChoices):
        NSE = "NSE", "National Stock Exchange"
        MCX = "MCX", "Multi Commodity Exchange"

    class ProductChoice(models.TextChoices):
        OPTIONS = "OPTIONS", "Options"
        FUTURES = "FUTURES", "Futures"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Format with country code: +919876543210",
    )
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Telegram Chat ID for alert notifications",
    )
    whatsapp_alerts_enabled = models.BooleanField(default=False)
    telegram_alerts_enabled = models.BooleanField(default=False)

    # Trading Preferences
    default_exchange = models.CharField(
        max_length=3,
        choices=ExchangeChoice.choices,
        default=ExchangeChoice.NSE,
    )
    default_product = models.CharField(
        max_length=10,
        choices=ProductChoice.choices,
        default=ProductChoice.OPTIONS,
    )
    favorite_symbols = models.JSONField(
        default=list,
        blank=True,
        help_text="List of favorite symbols, e.g. ['NIFTY', 'BANKNIFTY']",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Automatically create or save a profile whenever a User is saved."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()