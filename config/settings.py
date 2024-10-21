import socket
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# IP хоста на котором запускаем
HOST = socket.gethostbyname(socket.gethostname())

# Настройки RabbitMQ
RABBITMQ_HOST = HOST
RABBITMQ_PORT = 5672
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')

#INFLUX DB
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_URL = f"http://{HOST}:8086"
INFLUXDB_USERNAME = os.getenv('INFLUXDB_USERNAME')
INFLUXDB_PASSWORD = os.getenv('INFLUXDB_PASSWORD')

#MYSQL
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_DRIVER = os.getenv('DATABASE_DRIVER')
DATABASE_DIALECT = os.getenv('DATABASE_DIALECT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_URL = f"jdbc:mysql://{HOST}:3306/{DATABASE_NAME}?useSSL=false&rewriteBatchedStatements=true"

#Настройки NLU_PROXY
NLU_PROXY_EXCHANGE_INIT = 'svb-nlu-proxy-exchange'
NLU_PROXY_ROUTING_KEY_INIT = 'svb-nlu-proxy-init-key'
NLU_PROXY_ROUTING_KEY_REQUEST = 'svb-nlu-proxy-key-svb-nlu-proxy'
ROUTER_EXCHANGE_RESPONSE = 'svb-router-exchange'
ROUTER_NLU_PROXY_ROUTING_KEY_RESPONSE = 'svb-router-nlu-proxy-event-key'
ROUTER_NLU_PROXY_QUEUE_RESPONSE = 'svb-router-response-queue'

#Настройки AUDIT
AUDIT_EXCHANGE = 'svb-audit-exchange'
AUDIT_ROUTING_KEY = 'svb-audit-key'
AUDIT_ROUTING_KEY_SEARCH = 'svb-audit-search-key'


#Настройки Docker
DOCKER_IMAGE_NLU = os.getenv('DOCKER_IMAGE_NLU')
CONTAINER_NAME_NLU = os.getenv('CONTAINER_NAME_NLU')
DOCKER_IMAGE_AUDIT = os.getenv('DOCKER_IMAGE_AUDIT')
CONTAINER_NAME_AUDIT = os.getenv('CONTAINER_NAME_AUDIT')
DOCKER_IMAGE_RABBIT = os.getenv('DOCKER_IMAGE_RABBIT')
CONTAINER_NAME_RABBIT = os.getenv('CONTAINER_NAME_RABBIT')

