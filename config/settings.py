import socket

# IP хоста на котором запускаем
HOST = socket.gethostbyname(socket.gethostname())

# Настройки RabbitMQ
RABBITMQ_HOST = HOST
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'nlu'
RABBITMQ_PASSWORD = 'qwerty'
EXCHANGE_INIT = 'svb-nlu-proxy-exchange'
ROUTING_KEY_INIT = 'svb-nlu-proxy-init-key'
ROUTING_KEY_REQUEST = 'svb-nlu-proxy-key-svb-nlu-proxy'
EXCHANGE_RESPONSE = 'svb-router-exchange'
ROUTING_KEY_RESPONSE = 'svb-router-nlu-proxy-event-key'
QUEUE_RESPONSE = 'svb-router-response-queue'

# Настройки Docker
DOCKER_IMAGE_NLU = 'sm-nexus3.smiddle.lab:5000/smiddlegroup/svb-nlu-proxy:dev'
CONTAINER_NAME_NLU = 'svb-nlu-proxy'
DOCKER_IMAGE_RABBIT = 'rabbitmq:3.12.12-management-alpine'
CONTAINER_NAME_RABBIT = 'test_rabbitmq'

