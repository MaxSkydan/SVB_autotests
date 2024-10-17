import socket

# IP хоста на котором запускаем
HOST = socket.gethostbyname(socket.gethostname())

# Настройки RabbitMQ
RABBITMQ_HOST = HOST
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'nlu'
RABBITMQ_PASSWORD = 'qwerty'

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

#INFLUX DB
INFLUXDB_ORG = "my_org"
INFLUXDB_BUCKET = "my_bucket"
INFLUXDB_TOKEN = "my_token"
INFLUXDB_URL = "http://10.100.90.25:8086"

#MYSQL
DATABASE_URL="jdbc:mysql://10.100.90.25:3306/smiddle?useSSL=false&rewriteBatchedStatements=true"
DATABASE_USERNAME='root'
DATABASE_PASSWORD='root_password'
DATABASE_DRIVER='com.mysql.cj.jdbc.Driver'
DATABASE_DIALECT='org.hibernate.dialect.MySQLDialect'



# Настройки Docker
DOCKER_IMAGE_NLU = 'sm-nexus3.smiddle.lab:5000/smiddlegroup/svb-nlu-proxy:dev'
CONTAINER_NAME_NLU = 'svb-nlu-proxy'
DOCKER_IMAGE_AUDIT = 'sm-nexus3.smiddle.lab:5000/smiddlegroup/svb-audit:dev'
CONTAINER_NAME_AUDIT = 'svb-audit'
DOCKER_IMAGE_RABBIT = 'rabbitmq:3.12.12-management-alpine'
CONTAINER_NAME_RABBIT = 'test_rabbitmq'

