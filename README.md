# Slack Monday Bot

Бот для Slack, который раз в неделю отправляет в выбранный канал сообщение
с датой следующего понедельника.

Работает на Python (Flask + slack-sdk) и развёртывается на Railway.

## Переменные окружения

Нужно задать в Railway:

- `SLACK_BOT_TOKEN` — Bot User OAuth Token из Slack (начинается с `xoxb-...`)
- `SLACK_CHANNEL` — канал, куда писать, например `#general` или `#random`

## Расписание

Внутри `server.py` настраивается блок:

```python
TARGET_WEEKDAY = 4  # день недели (4 = пятница)
TARGET_HOUR = 10    # час (UTC)
TARGET_MINUTE = 0   # минута
