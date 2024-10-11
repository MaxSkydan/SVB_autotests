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
        return jsonify([]), 400


    # Start server
    thread = Thread(target=app.run, daemon=True, kwargs=dict(host=host, port=port))
    thread.start()
    time.sleep(2)

    # Provide app for testing
    yield app