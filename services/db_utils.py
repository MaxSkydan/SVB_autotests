import mysql.connector
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


def execute_query_mysql(sql_file: str) -> List[Tuple]:
    try:
        # Connect to the database
        conn = mysql.connector.connect(**mysql_database_config)
        print('Connected to MySQL database!')
    except mysql.connector.Error as err:
        print(f'Error connecting to database: {err}')
        return []  # Возвращаем пустой список в случае ошибки

    with open(sql_file, 'r') as file:
        sql = file.read()
    query = sql

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
