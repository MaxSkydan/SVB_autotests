import pytest
import time
import mysql.connector
from typing import List, Tuple, Optional
from config.settings import *

# Define the database credentials
database_config = {
    'user': DATABASE_USERNAME,
    'password': DATABASE_PASSWORD,
    'host': '127.0.0.1',
    'database': 'smiddle'
}

@pytest.fixture(scope='module')
def mysql_connection(mysql_container):
    # Подключаемся к базе данных MySQL
    connection = None
    for _ in range(10):  # Пробуем несколько раз, пока база не станет доступна
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                password="root_password",
                database="smiddle"
            )
            break
        except mysql.connector.Error:
            time.sleep(2)

    if connection is None:
        pytest.fail("Не удалось подключиться к базе данных")

    # Создаем пользователя и таблицы
    cursor = connection.cursor()
    cursor.execute("CREATE USER 'test_user'@'%' IDENTIFIED BY 'test_password';")
    cursor.execute("GRANT ALL PRIVILEGES ON smiddle.* TO 'test_user'@'%';")
    ##### тут добавляем таблицы неободимые сервису, спросить у Олексея
    # cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100));")
    #####
    connection.commit()

    yield connection

    # Закрываем соединение
    connection.close()


def execute_query(query: str) -> List[Tuple]:
    try:
        # Connect to the database
        conn = mysql.connector.connect(**database_config)
        print('Connected to Smiddle MySQL database!')
    except mysql.connector.Error as err:
        print(f'Error connecting to database: {err}')
        return []  # Возвращаем пустой список в случае ошибки

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
