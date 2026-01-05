from django.core.management.base import BaseCommand
from bot.tasks import check_subscriptions


class Command(BaseCommand):
    help = "Check subscriptions and send reminders"

    def handle(self, *args, **kwargs):
        check_subscriptions()
