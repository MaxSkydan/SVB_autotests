import json
import pytest
import time
from flask import Flask, request, jsonify
from threading import Event, Thread


# Событие для синхронизации завершения обработки запроса
flask_event = Event()

SENDER_ID = "d8bd8e5f-f309-4c13-a569-11c12cfc4b30:7739"

# Общая функция для формирования ответа и установки события
def send_response(response_data):
    flask_event.set()  # Устанавливаем событие после обработки
    return jsonify(response_data), 200


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
            with open("testdata/response_flask_data/rasa/response_map.json", 'r') as file:
                data = json.load(file)
            if message in data:
                return send_response(data[message])

        return jsonify([]), 400

    # Start server
    thread = Thread(target=app.run, daemon=True, kwargs=dict(host=host, port=port))
    thread.start()
    time.sleep(2)

    # Provide app for testing
    yield app
