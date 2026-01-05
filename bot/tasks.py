from datetime import date, timedelta
from .models import Subscription
from .views import send_message


def check_subscriptions():
    tomorrow = date.today() + timedelta(days=1)

    subs = Subscription.objects.filter(billing_date=tomorrow)

    for sub in subs:
        send_message(
            sub.user.telegram_id,
            f"Напоминание 🔔\nЗавтра списание: {sub.name}\nСумма: {sub.amount}"
        )
