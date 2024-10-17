import pytest
from services.db_utils import execute_query
from services.docker_setup import *
from services.rabbit_set import send_message_to_rabbitmq
from pytest_testrail.plugin import pytestrail



# Автотест для проверки всей цепочки обработки
@pytest.mark.usefixtures("setup_audit_docker")
@pytestrail.case('C2313')
def test_audit_income_call():
    # Отправляем тестовое сообщение через RabbitMQ
    send_message_to_rabbitmq("testdata/audit/income_call.json")

    # Проверяем данные в MySQL
    with open('testdata/audit/sql/income_call.sql', 'r') as file:
        sql = file.read()
    query = sql
    result = execute_query(query)

    # Проверяем корректность ответа
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])
