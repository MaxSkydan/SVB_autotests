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
    'port': 3306,
    'database': 'SMIDDLE'
}


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
            result = cursor.fetchone()

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f'Error executing query: {err}')
        result = []  # Возвращаем пустой список в случае ошибки

    finally:
        # Close the connection
        conn.close()

    return result
