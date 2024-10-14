import pytest
from services.flask_app import flask_event, app
from services.docker_setup import setup_docker
from services.rabbit_set import *



# Автотест для проверки всей цепочки обработки
@pytest.mark.usefixtures("setup_docker", "app")
def test_nlu_start_call():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/start_call.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "START_CALL"
    assert response["script"][0]["value"] == "Hello, I speak Ukrainian and English, how can I help you?"
    assert response["routingKey"] == "svb-nlu-proxy-key-svb-nlu-proxy"
    assert response["isUninterruptible"] is True

def test_nlu_2_types_response():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/speach_call.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "RESPONSE_GENERATED"
    assert (response["script"][0]["type"] == "TEXT" and
            response["script"][0]["value"] == "я не можу з цим допомогти , запитайте щось інше")
    assert (response["script"][1]["type"] == "FILE" and
            response["script"][1]["value"] == "greeting")
    assert response["isUninterruptible"] is False

def test_nlu_error_request():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/error_request.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is None

def test_nlu_error_response():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/error_response.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "ERROR"

def test_nlu_end_call_response():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/goodbye.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "END_CALL"
    assert response["script"][0]["type"] == "TEXT" and response["script"][0]["value"] == "Приємно було спілкуватись"

def test_nlu_redirect_call():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/redirect_call.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "REDIRECT_CALL"
    assert (response["script"][0]["type"] == "TEXT" and
            response["script"][0]["value"] == "Я вас не розумію. Перевожу на оператора")
    assert response["redirectNumber"] == "7777"

def test_nlu_user_redirect_call():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/user_redirect_call.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "USER_REDIRECT_CALL"
    assert (response["script"][0]["type"] == "TEXT" and
            response["script"][0]["value"] == "Добре. Перевожу на оператора")

if __name__ == "__main__":
    pytest.main([__file__])
