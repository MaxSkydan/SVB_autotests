import docker
import pytest
import time
import requests
from config.settings import *
from services.rabbit_set import is_rabbitmq_ready_amqp
from requests.exceptions import RequestException



# Проверка готовности сервиса с таймаутом
def wait_for_service_ready():
    # Определяем параметры опроса сервиса
    health_check_url = f"http://{HOST}:8804/actuator/health"  # Эндпоинт для проверки готовности сервиса
    timeout = 30  # Общее время ожидания в секундах
    interval = 1  # Интервал между попытками опроса в секундах

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_check_url)
            if response.status_code == 200:
                health_info = response.json()  # Получаем JSON-ответ
                # Проверяем статус RabbitMQ
                if health_info.get("components", {}).get("rabbit", {}).get("status") == "UP":
                    print("Сервис готов к работе!")
                    return True
        except RequestException as e:
            print(f"Ошибка запроса: {e}")

        print(f"Ожидание готовности сервиса... ({time.time() - start_time:.2f}s)")
        time.sleep(interval)

    print("Время ожидания истекло, сервис не готов.")
    return False



@pytest.fixture(scope="session", autouse=True)
def setup_rabbitmq_docker():
    client = docker.from_env()

    # Запуск контейнера RabbitMQ
    rabbitmq_container = client.containers.run(
        DOCKER_IMAGE_RABBIT,
        name=CONTAINER_NAME_RABBIT,
        ports={"5672/tcp": RABBITMQ_PORT, "15672/tcp": 15672},
        environment={
            "RABBITMQ_DEFAULT_USER": RABBITMQ_USER,
            "RABBITMQ_DEFAULT_PASS": RABBITMQ_PASSWORD
        },
        detach=True
    )

    # Проверка готовности RabbitMQ через AMQP-протокол
    for _ in range(30):  # 30 попыток с интервалом в 1 секунду
        if is_rabbitmq_ready_amqp():
            print("RabbitMQ готов к работе (AMQP).")
            break
        time.sleep(1)
    else:
        # Если не удалось подключиться за 30 секунд, выбрасываем исключение
        rabbitmq_container.stop()
        rabbitmq_container.remove()
        pytest.fail("RabbitMQ не удалось подготовиться за отведенное время.")

    yield

    # Остановка и удаление контейнерf после тестов

    rabbitmq_container.stop()
    rabbitmq_container.remove()



@pytest.fixture(scope="session", autouse=True)
def setup_nlu_proxy_docker(setup_rabbitmq_docker):
     client = docker.from_env()

     # Запуск тестируемого сервиса
     nlu_proxy_container = client.containers.run(
         DOCKER_IMAGE_NLU,
         name=CONTAINER_NAME_NLU,
         ports={"8080/tcp": 8804},
         environment={
             "RABBITMQ_ADDRESSES": f"{RABBITMQ_HOST}:{RABBITMQ_PORT}",
             "RABBITMQ_USERNAME": RABBITMQ_USER,
             "RABBITMQ_PASSWORD": RABBITMQ_PASSWORD
         },
         hostname=CONTAINER_NAME_NLU,
         detach=True
     )

     if wait_for_service_ready():
         print("Сервис успешно запущен и готов к работе.")
     else:
         print("Не удалось дождаться готовности сервиса. Проверьте настройки и состояние контейнера.")
         nlu_proxy_container.stop()
         nlu_proxy_container.remove()

         pytest.fail("Сервис не удалось подготовиться за отведенное время.")

     yield

     # Остановка и удаление контейнера после тестов

     nlu_proxy_container.stop()
     nlu_proxy_container.remove()
