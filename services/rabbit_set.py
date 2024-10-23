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
    # Декларация обмена для отправки на NLU Poxy
    channel.exchange_declare(exchange=NLU_PROXY_EXCHANGE_INIT,
                             exchange_type='direct', durable=True)

    # Декларация обмена для получения ответа от NLU Proxy
    channel.exchange_declare(exchange=ROUTER_EXCHANGE_RESPONSE,
                             exchange_type='direct', durable=True)

    # Декларация очереди для получения ответа от NLU Proxy
    channel.queue_declare(queue=ROUTER_NLU_PROXY_QUEUE_RESPONSE,
                          durable=True)

    # Привязка очереди к обмену для получения ответа от NLU Proxy
    channel.queue_bind(exchange=ROUTER_EXCHANGE_RESPONSE,
                       queue=ROUTER_NLU_PROXY_QUEUE_RESPONSE,
                       routing_key=ROUTER_NLU_PROXY_ROUTING_KEY_RESPONSE)

    # Декларация обмена для отправки на Audit
    channel.exchange_declare(exchange=AUDIT_EXCHANGE,
                             exchange_type='direct', durable=True)

# Функция для отправки тестового сообщения в RabbitMQ
def send_message_to_rabbitmq(message_data):

    connection, channel = connect_to_rabbitmq()
    setup_rabbitmq(channel)  # Убедиться, что обмен и очередь существуют

    # with open(message_file, 'r', encoding='utf-8') as file:
    #     message_data = json.load(file)

    data = message_data.get('message')
    exchange_name = message_data.get('exchange_name')
    routing_key = message_data.get('routing_key')
    message_type = message_data.get('message_type')

    message = data

    properties = pika.BasicProperties(
        content_type='application/json',
        content_encoding='UTF-8',
        delivery_mode=2,
        headers={'__TypeId__': message_type}
    )

    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=properties
    )

    connection.close()

# Ожидание ответа из RabbitMQ с таймаутом
def listen_for_response(queue, timeout=30, polling_interval=1):
    connection, channel = connect_to_rabbitmq()

    # Убедимся, что очередь существует
    setup_rabbitmq(channel)

    start_time = time.time()
    while time.time() - start_time < timeout:
        # Пытаемся получить сообщение из очереди
        method_frame, header_frame, body = channel.basic_get(queue=queue, auto_ack=True)

        if body:
            response = json.loads(body)
            connection.close()
            return response

        # Ждем перед следующей попыткой
        time.sleep(polling_interval)

    # Закрываем соединение, если не получили ответа
    connection.close()
    return None  # Если сообщение не пришло за время ожидания
