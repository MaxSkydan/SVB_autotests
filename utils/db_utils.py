import time
import json
import mysql.connector
from influxdb_client import InfluxDBClient
from typing import List, Tuple
from config.settings import *

# Define the database credentials
mysql_database_config = {
    'user': DATABASE_USERNAME,
    'password': DATABASE_PASSWORD,
    'host': HOST,
    'port': 3306,
    'database': DATABASE_NAME
}


def execute_query_mysql(sql_queries: str, trigger_word: str) -> List[Tuple]:
    try:
        # Connect to the database
        conn = mysql.connector.connect(**mysql_database_config)
        print('Connected to MySQL database!')
    except mysql.connector.Error as err:
        print(f'Error connecting to database: {err}')
        return []  # Возвращаем пустой список в случае ошибки

    # Чтение SQL-запросов из JSON-файла
    try:
        with open(sql_queries, 'r') as queries_file:
            queries_data = json.load(queries_file)
    except FileNotFoundError as e:
        print(f"Error: SQL queries file not found - {e}")
        return []

    # Поиск SQL-запроса по триггерному слову
    if trigger_word in queries_data:
        query = queries_data[trigger_word]  # SQL-запрос для триггера
    else:
        print(f"Trigger word '{trigger_word}' not found in SQL queries file.")
        return []

    try:
        # Create a cursor and execute the query
        with conn.cursor() as cursor:
            cursor.execute(query)

            # Fetch all results
            result = cursor.fetchall()

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f'Error executing query: {err}')
        result = []  # Возвращаем пустой список в случае ошибки

    finally:
        # Close the connection
        conn.close()

    return result


def execute_query_influx_db(influx_query):
    """
    Выполняет запрос к InfluxDB и возвращает массив словарей с результатами.

    Args:
        influx_query (str): Запрос на языке Flux.

    Returns:
        list: Массив словарей с результатами или пустой список, если произошла ошибка.
    """
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    except Exception as e:
        print(f"Ошибка создания клиента: {e}")
        return []

    # Проверяем подключение
    try:
        health = client.ping()
        if health:
            print("Connected to InfluxDB!")
        else:
            print("Подключение к InfluxDB не удалось.")
            return []
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return []

    # Выполняем запрос и обрабатываем результат
    try:
        query_api = client.query_api()
        result = query_api.query(influx_query)

        if not result:
            print("Запрос не вернул результатов.")
            return []

        # Обрабатываем данные из результата
        output = []
        for table in result:
            for record in table.records:
                output.append({
                    "result": record["result"],
                    "table": record["table"],
                    "_start": record["_start"],
                    "_stop": record["_stop"],
                    "_time": record["_time"],
                    "_value": record["_value"],
                    "_field": record["_field"],
                    "_measurement": record["_measurement"],
                    "isError": record["isError"],
                    "isRedirected": record["isRedirected"],
                    "projectId": record["projectId"],
                    "redirectInitiator": record["redirectInitiator"]
                })

        return output  # Возвращаем массив словарей

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []

    finally:
        # Закрываем клиент
        client.close()
