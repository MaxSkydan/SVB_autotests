import json
from services.db_utils import execute_query_mysql
from services.docker_setup import *
from services.rabbit_set import send_message_to_rabbitmq
from pytest_testrail.plugin import pytestrail



# # Автотест для проверки всей цепочки обработки
@pytest.mark.usefixtures("setup_audit_docker")
@pytestrail.case('C2313')
def test_audit_income_call():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/income_call.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/income_call.sql')

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][2] == '27603392-667f-4a00-ba87-9670636e6955'
    assert result[0][3] == 1
    assert result[0][4] == '7739'
    assert result[0][5] == '8621'
    assert result[0][8] == 'ARI_PROXY'
    assert result[0][9] == 'INCOME_CALL'


@pytestrail.case('C2314')
def test_audit_session_initialized():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/session_initialized.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/session_initialized.sql')

    # Проверяем корректность ответа
    assert result is not []
    assert result[1][8] == 'SPEECH_SERVICE'
    assert result[1][9] == 'SESSION_INITIALIZED'


@pytestrail.case('C2315')
def test_audit_start_call_ari_proxy():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/start_call_ari_proxy.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/start_call_ari_proxy.sql')

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'ARI_PROXY'
    assert result[0][9] == 'START_CALL'


@pytestrail.case('C2315')
def test_audit_start_call_nlu_proxy():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/start_call_nlu_proxy.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/start_call_nlu_proxy.sql')

    # Преобразуем значение из поля message в объект Python
    massage_json = json.loads(result[0][10])

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'START_CALL'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Hello, I speak Ukrainian and English, how can I help you?'


@pytestrail.case('C2315')
def test_audit_speech_service_rec():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/speech_rec_speech_service.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/speech_rec_speech_service.sql')


    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'SPEECH_SERVICE'
    assert result[0][9] == 'SPEECH_RECOGNIZED'
    assert result[0][10] == 'Розкажи, що ти вмієш.'


@pytestrail.case('C2315')
def test_audit_response_generated_2_types():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/response_generated_2_types.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/response_generated_2_types.sql')

    # Преобразуем значение из поля message в объект Python
    massage_json = json.loads(result[0][10])

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'RESPONSE_GENERATED'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'я не можу з цим допомогти , запитайте щось інше'
    assert massage_json[1]['type'] == 'FILE'
    assert massage_json[1]['value'] == 'greeting'


@pytestrail.case('C2315')
def test_audit_filler_insertion():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/filler_insertion_nlu.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/filler_insertion_nlu.sql')

    # Преобразуем значение из поля message в объект Python
    massage_json = json.loads(result[0][10])

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'FILLER_INSERTION'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Зачекайте хвилинку'


@pytestrail.case('C2315')
def test_audit_beep_command():
    execute_query_mysql('testdata/audit/sql/delete_records.sql')

    time.sleep(1)

    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/beep_command_nlu.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql('testdata/audit/sql/beep_command_nlu.sql')
    print(result)
    # Преобразуем значение из поля message в объект Python
    massage_json = json.loads(result[0][10])

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'BEEP'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Назвіть останні цифри лічильника після звукового сигналу'



if __name__ == "__main__":
    pytest.main([__file__])
