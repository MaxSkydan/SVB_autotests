import pytest
from services.flask_app import flask_event, app
from services.docker_setup import setup_rabbitmq_docker, setup_nlu_proxy_docker
from services.rabbit_set import *
from utils.wrappers import wrapper_nlu_proxy_service
from pytest_testrail.plugin import pytestrail



# Автотест для проверки всей цепочки обработки
@pytest.mark.usefixtures("setup_nlu_proxy_docker", "app")
@pytestrail.case('C2313', 'C2314', 'C2316', 'C2317', 'C2322', 'C2330', 'C2335', 'C2343', 'C2344')
def test_nlu_start_call():
    # Меняем данные для теста
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                    "start_call")
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq(message)

    # Ждем, пока событие на Flask не сработает
    flask_event.wait(timeout=10)

    # Слушаем ответ от RabbitMQ
    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    # Проверяем корректность ответа
    assert response is not None
    assert response["eventType"] == "START_CALL"
    assert response["script"][0]["value"] == "Hello, I speak Ukrainian and English, how can I help you?"
    assert response["routingKey"] == "svb-nlu-proxy-key-svb-nlu-proxy"
    assert response["isUninterruptible"] is True


@pytestrail.case('C2315', 'C2318', 'C2323', 'C2331', 'C2333', 'C2336', 'C2346')
def test_nlu_speech_call_2_types_response():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "speech_call_2_types_response")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "RESPONSE_GENERATED"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == "я не можу з цим допомогти , запитайте щось інше"
    assert response["script"][1]["type"] == "FILE"
    assert response["script"][1]["value"] == "greeting"
    assert response["isUninterruptible"] is False


@pytestrail.case('C2319')
def test_nlu_error_request():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "error_request")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is None


@pytestrail.case('C2320')
def test_nlu_end_call_request():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "end_call_request")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is None


@pytestrail.case('C2321', 'C2329', 'C2334', 'C2338')
def test_nlu_error_response():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "error_response")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "ERROR"


@pytestrail.case('C2328', 'C2337')
def test_nlu_end_call_response():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "end_call_response")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "END_CALL"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == "Приємно було спілкуватись"


@pytestrail.case('C2326', 'C2332', 'C2339', 'C2345')
def test_nlu_redirect_call():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "redirect_call")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "REDIRECT_CALL"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == "Я вас не розумію. Перевожу на оператора"
    assert response["redirectNumber"] == "7777"


@pytestrail.case('C2327', 'C2340')
def test_nlu_user_redirect_call():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "user_redirect_call")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "USER_REDIRECT_CALL"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == "Добре. Перевожу на оператора"


@pytestrail.case('C2324', 'C2341')
def test_nlu_beep_command():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "beep_command")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "BEEP"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == "Назвіть останні цифри лічильника після звукового сигналу"


@pytestrail.case('C2325', 'C2342', 'C2347')
def test_nlu_filler_insertion_command():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "filler_insertion_command")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "FILLER_INSERTION"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == "Дякую за запитання. Зачекайте хвилинку."
    assert response["isUninterruptible"] is True


@pytestrail.case('C2348', 'C2350')
def test_nlu_missing_number():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "missing_number")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "RESPONSE_GENERATED"
    assert response ["hostname"] == "svb-nlu-proxy"


@pytestrail.case('C2349')
def test_nlu_empty_string_response():
    message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
                                        "empty_string")

    send_message_to_rabbitmq(message)

    flask_event.wait(timeout=10)

    response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)

    assert response is not None
    assert response["eventType"] == "RESPONSE_GENERATED"
    assert response["script"][0]["type"] == "TEXT"
    assert response["script"][0]["value"] == ""
    assert response["script"][1]["type"] == "FILE"
    assert response["script"][1]["value"] == "greeting"


# @pytestrail.case('C2381')
# def test_nlu_unsupported_command_end_call_message():
#     message = wrapper_nlu_proxy_service("testdata/nlu_proxy/main_message_to_nlu_proxy.json",
#                                         "invalid_cmd_end_msg")
#
#     send_message_to_rabbitmq(message)
#
#     flask_event.wait(timeout=10)
#
#     response = listen_for_response(ROUTER_NLU_PROXY_QUEUE_RESPONSE)
#
#     assert response is not None
#     assert response["eventType"] == "END_CALL_MESSAGE"


if __name__ == "__main__":
    pytest.main([__file__])
