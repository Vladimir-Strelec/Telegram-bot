from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    state = models.CharField(
        max_length=50,
        default="idle"
    )
    username = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.telegram_id)


class Subscription(models.Model):
    name = models.CharField(max_length=255, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Сумма списания"
    )

    currency = models.CharField(
        max_length=3,
        default="EUR"
    )

    billing_date = models.DateField(
        help_text="Дата следующего списания"
    )

    remind_days_before = models.PositiveIntegerField(
        default=3,
        help_text="За сколько дней напоминать"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} ({self.user.telegram_id})"