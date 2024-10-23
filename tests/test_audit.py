import json
from utils.db_utils import *
from utils.wrappers import wrapper_audit_service
from services.docker_setup import *
from services.rabbit_set import send_message_to_rabbitmq
from pytest_testrail.plugin import pytestrail
from services.rabbit_set import *



# # Автотест для проверки всей цепочки обработки
@pytest.mark.usefixtures("setup_audit_docker")
@pytestrail.case('C2351', 'C2352', 'C2353', 'C2368', 'C2372', 'C2374')
def test_audit_income_call():
    # Меняем данные для теста
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "income_call")
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq(message)

    time.sleep(1)

    # Проверяем данные в MySQL
    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                    "income_call")

    # Проверяем корректность ответа
    assert result
    assert result[0][2] == '27603392-667f-4a00-ba87-9670636e6955'
    assert result[0][8] == 'ARI_PROXY'
    assert result[0][9] == 'INCOME_CALL'


@pytestrail.case('C2354', 'C2370', 'C2371')
def test_audit_session_initialized():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "session_initialized")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "session_initialized")

    assert result
    assert result[0][4] == '7739'
    assert result[0][5] == '8621'
    assert result[1][8] == 'SPEECH_SERVICE'
    assert result[1][9] == 'SESSION_INITIALIZED'


@pytestrail.case('C2355', 'C2369')
def test_audit_start_call_ari_proxy():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "start_call_ari_proxy")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "start_call_ari_proxy")

    assert result
    assert result[0][3] == 1
    assert result[0][8] == 'ARI_PROXY'
    assert result[0][9] == 'START_CALL'


@pytestrail.case('C2356', 'C2366')
def test_audit_start_call_nlu_proxy():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "start_call_nlu_proxy")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "start_call_nlu_proxy")

    # Преобразуем значение из поля message в объект Python
    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'START_CALL'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Hello, I speak Ukrainian and English, how can I help you?'


@pytestrail.case('C2357')
def test_audit_speech_service_rec():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "speech_rec_speech_service")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "speech_rec_speech_service")

    assert result
    assert result[0][8] == 'SPEECH_SERVICE'
    assert result[0][9] == 'SPEECH_RECOGNIZED'
    assert result[0][10] == 'Розкажи, що ти вмієш.'


@pytestrail.case('C2358', 'C2367')
def test_audit_response_generated_2_types():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "response_generated_2_types")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "response_generated_2_types")

    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'RESPONSE_GENERATED'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'я не можу з цим допомогти , запитайте щось інше'
    assert massage_json[1]['type'] == 'FILE'
    assert massage_json[1]['value'] == 'greeting'


@pytestrail.case('C2359')
def test_audit_filler_insertion():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "filler_insertion_nlu")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "filler_insertion_nlu")

    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'FILLER_INSERTION'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Зачекайте хвилинку'


@pytestrail.case('C2360')
def test_audit_beep_command():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "beep_command_nlu")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "beep_command_nlu")

    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'BEEP'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Назвіть останні цифри лічильника після звукового сигналу'


@pytestrail.case('C2361', 'C2373')
def test_audit_redirect_call_with_number():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "redirect_call_with_number")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "redirect_call_with_number")

    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][7] == '7777'
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'REDIRECT_CALL'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Я вас не розумію. Перевожу на оператора'


@pytestrail.case('C2364')
def test_audit_end_call_nlu():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "end_call_nlu")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "end_call_nlu")

    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'END_CALL'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'На все добре'


@pytestrail.case('C2365')
def test_audit_end_call_message_speech_service():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "end_call_message_speech_service")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "end_call_message_speech_service")


    assert result
    assert result[0][8] == 'SPEECH_SERVICE'
    assert result[0][9] == 'END_CALL_MESSAGE'


    # Делаем запрос в InfluxDB
    result_influx = execute_query_influx_db(f"""
                    from(bucket: "{INFLUXDB_BUCKET}")
                    |> range(start: -1h)
                    """)
    print(result_influx)


@pytestrail.case('C2362', 'C2376')
def test_audit_user_redirect_call_without_number():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "user_redirect_call_without_number")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "user_redirect_call_without_number")

    massage_json = json.loads(result[0][10])


    assert result
    assert result[0][7] is None
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'USER_REDIRECT_CALL'
    assert massage_json[0]['type'] == 'TEXT'
    assert massage_json[0]['value'] == 'Добре. Перевожу на оператора'


@pytestrail.case('C2363')
def test_audit_error_command_nlu():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "error_command_nlu")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "error_command_nlu")


    assert result
    assert result[0][8] == 'NLU_PROXY'
    assert result[0][9] == 'ERROR'
    assert result[0][10] is None


@pytestrail.case('C2377')
def test_audit_error_command_speech_service():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "error_command_speech_service")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "error_command_speech_service")


    assert result
    assert result[0][8] == 'SPEECH_SERVICE'
    assert result[0][9] == 'ERROR'
    assert result[0][10] is None


@pytestrail.case('C2378')
def test_audit_error_command_ari_proxy():
    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "error_command_ari_proxy")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "error_command_ari_proxy")


    assert result
    assert result[0][8] == 'ARI_PROXY'
    assert result[0][9] == 'ERROR'
    assert result[0][10] is None


@pytestrail.case('C2379')
def test_audit_unknown_command():
    # Удаляем все записи из MySql
    execute_query_mysql("testdata/audit/sql_queries_audit.json","delete_records")

    time.sleep(1)

    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "unknown_command")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "select_all")

    assert not result


@pytestrail.case('C2380')
def test_audit_missing_number():
    # Удаляем все записи из MySql
    execute_query_mysql("testdata/audit/sql_queries_audit.json","delete_records")

    time.sleep(1)

    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "missing_number")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "select_all")

    assert not result


@pytestrail.case('C2365')
def test_audit_end_call_speech_service():
    # Удаляем все записи из MySql
    execute_query_mysql("testdata/audit/sql_queries_audit.json","delete_records")

    time.sleep(1)

    message = wrapper_audit_service("testdata/audit/main_message_to_audit.json",
                                    "end_call_speech_service")

    send_message_to_rabbitmq(message)

    time.sleep(1)

    result = execute_query_mysql("testdata/audit/sql_queries_audit.json",
                                 "end_call_speech_service")
    print(result)


    assert result
    assert result[0][8] == 'SPEECH_SERVICE'
    assert result[0][9] == 'END_CALL'
    assert result[0][10] == 'Бувай'



if __name__ == "__main__":
    pytest.main([__file__])
