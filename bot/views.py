import json
from datetime import date, datetime
from decimal import Decimal

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Subscription
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")  # твой токен из .env


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


@csrf_exempt
def webhook(request):

    if request.method != 'POST':
        return JsonResponse({'ok': True})

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': True})

    message = data.get('message')
    if not message:
        return JsonResponse({'ok': True})

    chat = message.get('chat', {})
    telegram_id = chat.get('id')
    username = chat.get('username', '')

    if not telegram_id:
        return JsonResponse({'ok': True})

    User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'username': username}
    )

    commands = {
        "/start": response_on_start,
        "/add": response_on_add,
    }

    text = message.get("text")
    if not text:
        return JsonResponse({'ok': True})

    text = text.strip()
    command = text.split()[0]

    handler = commands.get(command)

    if handler:
        handler(telegram_id)
    else:
        handle_text_message(telegram_id, text)

    return JsonResponse({'ok': True})


def response_on_start(telegram_id):
    send_message(telegram_id, "Привет! Я буду напоминать о твоих подписках. Используй /add, чтобы добавить подписку.")


def response_on_add(telegram_id):
    user = User.objects.get(telegram_id=telegram_id)
    user.state = "awaiting_subscription_name"
    user.save()

    send_message(telegram_id, "Введите название подписки (например: Netflix)")


def handle_text_message(telegram_id, text):
    user = User.objects.get(telegram_id=telegram_id)

    if user.state == "awaiting_subscription_name":
        awaiting_subscriptions(user, telegram_id, text)

    elif user.state == "awaiting_amount":
        awaiting_amount(user, telegram_id, text)

    elif user.state == "billing_date":
        billing_date(user, telegram_id, text)


def awaiting_subscriptions(user, telegram_id, text):
    Subscription.objects.create(
        user=user,
        name=text,
        amount=0,
        billing_date=date.today()
    )
    user.state = "awaiting_amount"
    user.save()

    send_message(telegram_id, "Сколько стоит подписка?")
    return


def awaiting_amount(user, telegram_id, text):
    try:
        amount = Decimal(text.replace(",", "."))
    except Exception:
        send_message(
            telegram_id,
            "Введите сумму числом.\nПример: 9.99"
        )
        return

    sub = Subscription.objects.filter(user=user).last()

    if not sub:
        send_message(telegram_id, "Ошибка: подписка не найдена.")
        user.state = "idle"
        user.save()
        return

    sub.amount = amount
    sub.save()

    user.state = "billing_date"
    user.save()

    send_message(telegram_id, "Введите дату в формате ДД.ММ.ГГГГ\nНапример: 15.01.2026")
    return


def billing_date(user, telegram_id, text):
    print(text)
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        send_message(
            telegram_id,
            "Неверный формат даты ❌\nВведите дату в формате ДД.ММ.ГГГГ\nНапример: 15.01.2026"
        )
        return

    sub = Subscription.objects.filter(user=user).last()
    if not sub:
        send_message(telegram_id, "Ошибка: подписка не найдена")
        user.state = "idle"
        user.save()
        return

    sub.billing_date = date_obj
    sub.save()

    user.state = "idle"
    user.save()

    send_message(
        telegram_id,
        f"Готово ✅\nДата списания: {date_obj.strftime('%d.%m.%Y')}"
    )



