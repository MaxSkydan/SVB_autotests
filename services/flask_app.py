import time
import pytest
from flask import Flask, request, jsonify
from threading import Event, Thread


# Событие для синхронизации завершения обработки запроса
flask_event = Event()


@pytest.fixture(scope='session', autouse=True)
def app() -> Flask:
    host = '0.0.0.0'
    port = 5005

    app = Flask(__name__)

    @app.route('/webhooks/rest/webhook', methods=['POST'])
    def rasa_webhook():
        data = request.json
        if data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and data["message"] == "#COMMAND:START_CALL":
            response = [
                {
                    "text": "Hello, I speak Ukrainian and English, how can I help you?",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                },
                {
                    "text": "#UNINTERRUPTIBLE",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                 }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif (data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and
              data["message"] == "Де подивитись гарний фільм?"):
            response = [
                {
                    "text": "я не можу з цим допомогти , запитайте щось інше",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                },
                {
                    "text": "#FILE:greeting",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                 }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and data["message"] == "Error":
            response = [
                {
                    "text": None,
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and data["message"] == "#COMMAND:ERROR":
            response = [
                {
                    "text": "#COMMAND:ERROR",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif (data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and
              data["message"] == "На все добре. До побачення"):
            response = [
                {
                    "text": "Приємно було спілкуватись",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                },
                {
                    "text": "#COMMAND:END_CALL",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif (data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and
              data["message"] == "Щось нове та цікаве"):
            response = [
                {
                    "text": "Я вас не розумію. Перевожу на оператора",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                },
                {
                    "text": "#COMMAND:REDIRECT_CALL:7777",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif (data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and
              data["message"] == "Переведи мене на оператора"):
            response = [
                {
                    "text": "Добре. Перевожу на оператора",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                },
                {
                    "text": "#COMMAND:USER_REDIRECT_CALL",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and data["message"] == "#COMMAND:END_CALL":
            response = [
                {
                    "text": "#COMMAND:END_CALL",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        elif data["sender"] == "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739" and data["message"] == "Лічильник":
            response = [
                {
                    "text": "Назвіть останні цифри лічильника після звукового сигналу",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                },
                {
                    "text": "#COMMAND:BEEP",
                    "recipient_id": "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"
                }
            ]
            flask_event.set()  # Устанавливаем событие после обработки
            return jsonify(response), 200
        return jsonify([]), 400


    # Start server
    thread = Thread(target=app.run, daemon=True, kwargs=dict(host=host, port=port))
    thread.start()
    time.sleep(2)

    # Provide app for testing
    yield app