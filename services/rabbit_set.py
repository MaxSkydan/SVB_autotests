import pika, pika.exceptions
import json
import time
from config.settings import *



# Проверка готовности сервиса
def is_rabbitmq_ready_amqp():
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
        )
        connection.close()
        return True
    except pika.exceptions.AMQPConnectionError:
        return False


# Подключение к RabbitMQ
def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()
    return connection, channel

# Создание обменов и очередей
def setup_rabbitmq(channel):
    # Декларация обмена для отправки
    channel.exchange_declare(exchange=EXCHANGE_INIT, exchange_type='direct', durable=True)

    # Декларация обмена для получения ответа
    channel.exchange_declare(exchange=EXCHANGE_RESPONSE, exchange_type='direct', durable=True)

    # Декларация очереди для получения ответа
    channel.queue_declare(queue=QUEUE_RESPONSE, durable=True)

    # Привязка очереди к обмену
    channel.queue_bind(exchange=EXCHANGE_RESPONSE, queue=QUEUE_RESPONSE, routing_key=ROUTING_KEY_RESPONSE)

# Функция для отправки тестового сообщения в RabbitMQ
def send_message_to_rabbitmq(file_path, routing_key=ROUTING_KEY_REQUEST):
    connection, channel = connect_to_rabbitmq()
    setup_rabbitmq(channel)  # Убедиться, что обмен и очередь существуют

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    message = data

    properties = pika.BasicProperties(
        content_type='application/json',
        content_encoding='UTF-8',
        delivery_mode=2,
        headers={'__TypeId__': 'com.smiddle.svb.common.core.model.event.RouterEvent'}
    )

    channel.basic_publish(
        exchange=EXCHANGE_INIT,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=properties
    )

    connection.close()

# Ожидание ответа из RabbitMQ с таймаутом
def listen_for_response(timeout=30, polling_interval=1):
    connection, channel = connect_to_rabbitmq()

    # Убедимся, что очередь существует
    setup_rabbitmq(channel)

    start_time = time.time()
    while time.time() - start_time < timeout:
        # Пытаемся получить сообщение из очереди
        method_frame, header_frame, body = channel.basic_get(queue=QUEUE_RESPONSE, auto_ack=True)

        if body:
            response = json.loads(body)
            connection.close()
            return response

        # Ждем перед следующей попыткой
        time.sleep(polling_interval)

    # Закрываем соединение, если не получили ответа
    connection.close()
    return None  # Если сообщение не пришло за время ожидания
