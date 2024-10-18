import docker
import pytest
import time
import requests
import mysql.connector
from config.settings import *
from services.rabbit_set import is_rabbitmq_ready_amqp
from requests.exceptions import RequestException
from influxdb_client import InfluxDBClient



# Проверка готовности сервиса с таймаутом
def wait_for_service_ready(port):
    # Определяем параметры опроса сервиса
    health_check_url = f"http://{HOST}:{port}/actuator/health"  # Эндпоинт для проверки готовности сервиса
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


@pytest.fixture(scope="module", autouse=True)
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


@pytest.fixture(scope='module', autouse=True)
def setup_mysql_container():
    client = docker.from_env()

    # Поднимаем контейнер с MySQL
    mysql_container = client.containers.run(
        'mysql:8.0',
        environment={
            'MYSQL_ROOT_PASSWORD': DATABASE_PASSWORD,
            'MYSQL_DATABASE': DATABASE_NAME,
            'MYSQL_ROOT_HOST': '%'
        },
        ports={'3306/tcp': 3306},
        detach=True
    )

    # Ожидаем, пока MySQL полностью запустится
    for _ in range(10):  # Пробуем несколько раз
        try:
            connection = mysql.connector.connect(
                host=HOST,
                port=3306,
                user=DATABASE_USERNAME,
                password=DATABASE_PASSWORD,
                database=DATABASE_NAME
            )
            connection.close()
            print("Подключение к базе данных MySQL успешно установлено!")
            break
        except mysql.connector.Error as e:
             print(f"Ошибка подключения: {e}")  # Выводим ошибку для отладки
             time.sleep(2)

    yield mysql_container

    # Останавливаем и удаляем контейнер после тестов
    mysql_container.stop()
    mysql_container.remove()


@pytest.fixture(scope='module', autouse=True)
def setup_influxdb_container():
    client = docker.from_env()

    # Запускаем контейнер с InfluxDB
    influxdb_container = client.containers.run(
        'influxdb:latest',
        environment={
            'DOCKER_INFLUXDB_INIT_MODE': 'setup',
            'DOCKER_INFLUXDB_INIT_USERNAME': INFLUXDB_USERNAME,
            'DOCKER_INFLUXDB_INIT_PASSWORD': INFLUXDB_PASSWORD,
            'DOCKER_INFLUXDB_INIT_ORG': INFLUXDB_ORG,
            'DOCKER_INFLUXDB_INIT_BUCKET': INFLUXDB_BUCKET,
            'DOCKER_INFLUXDB_INIT_ADMIN_TOKEN': INFLUXDB_TOKEN,
        },
        ports={'8086/tcp': 8086},
        detach=True
    )

    # Ожидаем, пока InfluxDB полностью запустится
    for _ in range(10):  # Пробуем несколько раз, пока база не станет доступна
        try:
            connect = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
            # Проверяем успешность подключения
            health = client.ping()
            if health:
                connect.close()
                print("Подключение к базе данных InfluxDB успешно установлено!")
                break
        except Exception as e:
                print(f"Ошибка подключения: {e}")  # Выводим ошибку для отладки
                time.sleep(2)

    yield influxdb_container

    # Останавливаем и удаляем контейнер после тестов
    influxdb_container.stop()
    influxdb_container.remove()


@pytest.fixture(scope="module", autouse=True)
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

     if wait_for_service_ready(8804):
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



@pytest.fixture(scope="module", autouse=True)
def setup_audit_docker(setup_rabbitmq_docker, setup_mysql_container, setup_influxdb_container):
     client = docker.from_env()

     # Запуск тестируемого сервиса
     audit_container = client.containers.run(
         DOCKER_IMAGE_AUDIT,
         name=CONTAINER_NAME_AUDIT,
         ports={"8080/tcp": 8805},
         environment={
             "RABBITMQ_ADDRESSES": f"{RABBITMQ_HOST}:{RABBITMQ_PORT}",
             "RABBITMQ_USERNAME": RABBITMQ_USER,
             "RABBITMQ_PASSWORD": RABBITMQ_PASSWORD,
             "INFLUX_URL": INFLUXDB_URL,
             "INFLUX_TOKEN": INFLUXDB_TOKEN,
             "INFLUX_ORG": INFLUXDB_ORG,
             "INFLUX_BUCKET": INFLUXDB_BUCKET,
             "DATABASE_URL": DATABASE_URL,
             "DATABASE_USERNAME": DATABASE_USERNAME,
             "DATABASE_PASSWORD": DATABASE_PASSWORD,
             "DATABASE_DRIVER": DATABASE_DRIVER,
             "DATABASE_DIALECT": DATABASE_DIALECT
         },
         hostname=CONTAINER_NAME_AUDIT,
         detach=True
     )

     if wait_for_service_ready(8805):
         print("Сервис успешно запущен и готов к работе.")
         # Запрос на включение Debug режима
         # requests.post(f'http://{HOST}:8805/actuator/loggers/com.smiddle', json={"configuredLevel": "DEBUG"})
     else:
         print("Не удалось дождаться готовности сервиса. Проверьте настройки и состояние контейнера.")
         audit_container.stop()
         audit_container.remove()

         pytest.fail("Сервис не удалось подготовиться за отведенное время.")

     yield

     # Остановка и удаление контейнера после тестов
     audit_container.stop()
     audit_container.remove()
