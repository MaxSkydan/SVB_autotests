import time
import pytest
from flask import Flask, request, jsonify
from threading import Event, Thread


# Событие для синхронизации завершения обработки запроса
flask_event = Event()

SENDER_ID = "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
RECIPIENT_ID = "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"

# Общая функция для формирования ответа и установки события
def send_response(response_data):
    flask_event.set()  # Устанавливаем событие после обработки
    return jsonify(response_data), 200

# Словарь для маппинга сообщений на соответствующие ответы
response_map = {
    "#COMMAND:START_CALL": [
        {"text": "Hello, I speak Ukrainian and English, how can I help you?", "recipient_id": RECIPIENT_ID},
        {"text": "#UNINTERRUPTIBLE", "recipient_id": RECIPIENT_ID}
    ],
    "Де подивитись гарний фільм?": [
        {"text": "я не можу з цим допомогти , запитайте щось інше", "recipient_id": RECIPIENT_ID},
        {"text": "#FILE:greeting", "recipient_id": RECIPIENT_ID}
    ],
    "Error": [
        {"text": None, "recipient_id": RECIPIENT_ID}
    ],
    "#COMMAND:ERROR": [
        {"text": "#COMMAND:ERROR", "recipient_id": RECIPIENT_ID}
    ],
    "На все добре. До побачення": [
        {"text": "Приємно було спілкуватись", "recipient_id": RECIPIENT_ID},
        {"text": "#COMMAND:END_CALL", "recipient_id": RECIPIENT_ID}
    ],
    "Щось нове та цікаве": [
        {"text": "Я вас не розумію. Перевожу на оператора", "recipient_id": RECIPIENT_ID},
        {"text": "#COMMAND:REDIRECT_CALL:7777", "recipient_id": RECIPIENT_ID}
    ],
    "Переведи мене на оператора": [
        {"text": "Добре. Перевожу на оператора", "recipient_id": RECIPIENT_ID},
        {"text": "#COMMAND:USER_REDIRECT_CALL", "recipient_id": RECIPIENT_ID}
    ],
    "#COMMAND:END_CALL": [
        {"text": "#COMMAND:END_CALL", "recipient_id": RECIPIENT_ID}
    ],
    "Лічильник": [
        {"text": "Назвіть останні цифри лічильника після звукового сигналу", "recipient_id": RECIPIENT_ID},
        {"text": "#COMMAND:BEEP", "recipient_id": RECIPIENT_ID}
    ]
}


@pytest.fixture(scope='session', autouse=True)
def app() -> Flask:
    host = '0.0.0.0'
    port = 5005

    app = Flask(__name__)

    @app.route('/webhooks/rest/webhook', methods=['POST'])
    def rasa_webhook():
        data = request.json

        # Проверяем sender и находим соответствующий ответ по message
        if data.get("sender") == SENDER_ID:
            message = data.get("message")
            if message in response_map:
                return send_response(response_map[message])

        return jsonify([]), 400

    # Start server
    thread = Thread(target=app.run, daemon=True, kwargs=dict(host=host, port=port))
    thread.start()
    time.sleep(2)

    # Provide app for testing
    yield app
