import pytest
from services.flask_app import flask_event, app
from services.docker_setup import setup_docker
from services.rabbit_set import send_message_to_rabbitmq, listen_for_response



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
    assert response["isUninterruptible"] is True

def test_nlu_start_call2():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/nlu/start_call_short.json")

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response()

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "START_CALL"
    assert response["script"][0]["value"] == "Hello, I speak Ukrainian and English, how can I help you?"
    assert response["isUninterruptible"] is True

if __name__ == "__main__":
    pytest.main([__file__])
