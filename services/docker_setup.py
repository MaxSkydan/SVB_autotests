import docker
import pytest
import time
from config.settings import *
from services.rabbit_set import is_rabbitmq_ready_amqp, wait_for_service_ready



@pytest.fixture(scope="session", autouse=True)
def setup_docker():
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

    # Запуск тестируемого сервиса
    test_service_container = client.containers.run(
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
        test_service_container.stop()
        test_service_container.remove()
        rabbitmq_container.stop()
        rabbitmq_container.remove()

        pytest.fail("Сервис не удалось подготовиться за отведенное время.")


    yield

    # Остановка и удаление контейнеров после тестов

    test_service_container.stop()
    test_service_container.remove()
    rabbitmq_container.stop()
    rabbitmq_container.remove()