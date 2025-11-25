import os
import threading
import time
from datetime import date, datetime, timedelta

from flask import Flask
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

# Токен бота и канал берём из переменных окружения
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#general")

client = WebClient(token=SLACK_BOT_TOKEN)


def get_next_monday(from_date=None):
    """Вернуть дату ближайшего ПОНЕДЕЛЬНИКА после указанной даты (или сегодня)."""
    if from_date is None:
        from_date = date.today()
    weekday = from_date.weekday()  # 0=понедельник, 6=воскресенье
    days_until_monday = (7 - weekday) % 7
    if days_until_monday == 0:
        days_until_monday = 7  # если сегодня понедельник — берём следующий
    return from_date + timedelta(days=days_until_monday)


def send_monday_message():
    """Отправить сообщение в Slack с датой следующего понедельника."""
    if not SLACK_BOT_TOKEN:
        print("SLACK_BOT_TOKEN не задан, сообщение не отправлено")
        return

    next_mon = get_next_monday()
    text = f"Напоминание: следующий понедельник — *{next_mon.strftime('%d.%m.%Y')}* :calendar:"

    try:
        resp = client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
        print("Сообщение отправлено:", resp.get('ts'), text)
    except SlackApiError as e:
        print("Ошибка Slack:", e.response.get("error"))


def seconds_until_next_run(target_weekday: int, hour: int, minute: int):
    """
    Сколько секунд до следующего запуска:
    target_weekday: 0=понедельник, 6=воскресенье
    """
    now = datetime.utcnow()  # Railway обычно работает в UTC
    today_weekday = now.weekday()

    days_ahead = (target_weekday - today_weekday) % 7
    run_date = (now + timedelta(days=days_ahead)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    if run_date <= now:
        run_date += timedelta(days=7)

    delta = run_date - now
    return delta.total_seconds()


def scheduler_loop():
    """
    Фоновый планировщик:
    раз в неделю (по расписанию) отправляет сообщение.
    """
    # НАСТРОЙКА РАСПИСАНИЯ:
    # 0=понедельник ... 4=пятница, 6=воскресенье
    TARGET_WEEKDAY = 4     # 4 = пятница
    TARGET_HOUR = 10       # час (UTC)
    TARGET_MINUTE = 0      # минута

    while True:
        wait_sec = seconds_until_next_run(TARGET_WEEKDAY, TARGET_HOUR, TARGET_MINUTE)
        print(f"Ждём {wait_sec/3600:.2f} ч до следующей отправки...")
        time.sleep(wait_sec)
        send_monday_message()
        time.sleep(5)


@app.route("/")
def index():
    return "Slack Monday Bot работает ✅"


@app.route("/health")
def health():
    return "OK", 200


def start_scheduler():
    """Запуск планировщика в отдельном потоке."""
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()


if __name__ == "__main__":
    # Запускаем фонового планировщика
    start_scheduler()

    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
