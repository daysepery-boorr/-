import requests
import time
import os

# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.environ["BOT_TOKEN"]

CHANNEL = "@fhdhdjwowow"

API_URL = "https://neptun.in.ua/api/v1/alerts"

# ==============================================

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def telegram(method, data=None):
    response = requests.post(
        f"{TG_URL}/{method}",
        json=data or {},
        timeout=20
    )

    response.raise_for_status()
    return response.json()


def get_alert_state():
    response = requests.get(
        API_URL,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    # Житомирская область
    for alert in data.get("oblasts", []):
        if alert.get("name") == "Житомирська область":
            return True

    # Районы Житомирской области
    for alert in data.get("raions", []):
        if alert.get("oblast") == "Житомирська область":
            return True

    return False


def publish_alert(alert_started):

    if alert_started:
        message = (
            "🚨 ПОВІТРЯНА ТРИВОГА\n\n"
            "Житомирська область"
        )
    else:
        message = (
            "🟢 ВІДБІЙ ПОВІТРЯНОЇ ТРИВОГИ\n\n"
            "Житомирська область"
        )

    result = telegram(
        "sendMessage",
        {
            "chat_id": CHANNEL,
            "text": message
        }
    )

    if result.get("ok"):
        print("Сообщение опубликовано в канал.")
    else:
        print(
            "Ошибка публикации:",
            result.get("description", "Неизвестная ошибка")
        )


def main():

    print("Бот запущен.")

    try:
        last_state = get_alert_state()

        print(
            "Текущее состояние:",
            "ТРЕВОГА" if last_state else "ОТБОЙ"
        )

    except Exception as e:
        print("Ошибка API:", e)
        last_state = None

    while True:

        try:
            current_state = get_alert_state()

            if (
                last_state is not None
                and current_state != last_state
            ):

                print(
                    "Состояние изменилось:",
                    "ТРЕВОГА" if current_state else "ОТБОЙ"
                )

                publish_alert(current_state)

            last_state = current_state

        except Exception as e:
            print("Ошибка проверки API:", e)

        # Проверка каждые 30 секунд
        time.sleep(30)


if __name__ == "__main__":
    main()
