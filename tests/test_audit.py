from services.db_utils import execute_query_mysql
from services.docker_setup import *
from services.rabbit_set import send_message_to_rabbitmq
from pytest_testrail.plugin import pytestrail



# Автотест для проверки всей цепочки обработки
@pytest.mark.usefixtures("setup_audit_docker")
@pytestrail.case('C2313')
def test_audit_income_call():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/income_call.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    with open('testdata/audit/sql/income_call.sql', 'r') as file:
        sql = file.read()
    query = sql
    result = execute_query_mysql(query)
    print(result)

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
    with open('testdata/audit/sql/session_initialized.sql', 'r') as file:
        sql = file.read()
    query = sql
    result = execute_query_mysql(query)
    print(result)

    # Проверяем корректность ответа
    assert result is not []
    assert result[1][8] == 'SPEECH_SERVICE'
    assert result[1][9] == 'SESSION_INITIALIZED'


@pytestrail.case('C2315')
def test_audit_start_call():
    with open('testdata/audit/sql/delete_records.sql', 'r') as file:
        sql = file.read()
    query = sql
    execute_query_mysql(query)

    time.sleep(1)

    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/start_call.json")

    time.sleep(1)

    # Проверяем данные в MySQL
    with open('testdata/audit/sql/start_call.sql', 'r') as file:
        sql = file.read()
    query = sql
    result = execute_query_mysql(query)
    print(result)

    # Проверяем корректность ответа
    assert result is not []
    assert result[0][8] == 'ARI_PROXY'
    assert result[0][9] == 'START_CALL'


if __name__ == "__main__":
    pytest.main([__file__])
