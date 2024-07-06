import psycopg2
from psycopg2 import pool
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
import os


# Создание пула соединений
connection_pool = pool.SimpleConnectionPool(
    1, 10, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME
)

def check_existing_record(link):
    query = "SELECT id FROM vacancies WHERE link = %s"

    connection = connection_pool.getconn()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (link,))
            result = cursor.fetchone()
            if result:
                return True, result[0]  # Возвращаем True и ID записи
            else:
                return False, None  # Возвращаем False, если запись не найдена
    finally:
        connection_pool.putconn(connection)

def db_insert(title, price, price_from, price_to, company, city, link):
    exists, existing_id = check_existing_record(link)
    if exists:
        return existing_id  # Возвращаем ID существующей записи

    query = "INSERT INTO vacancies (title, price, price_from, price_to, company, city, link) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"

    # Получение соединения из пула
    connection = connection_pool.getconn()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (title, price, price_from, price_to, company, city, link))
            inserted_id = cursor.fetchone()[0]  # Получаем ID вставленной записи
            connection.commit()
            return inserted_id  # Возвращаем ID успешно вставленной записи
    finally:
        # Возвращение соединения в пул
        connection_pool.putconn(connection)

def get_vacancy_from_db(vacancy_id):
    query = "SELECT title, price, price_from, price_to, company, city, link FROM vacancies WHERE id = %s"

    # Получение соединения с базой данных
    connection = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (vacancy_id,))
            result = cursor.fetchone()
            if result:
                title, price, price_from, price_to, company, city, link = result
                # Возвращаем словарь с данными о вакансии
                return {
                    'id': vacancy_id,
                    'title': title,
                    'price': price,
                    'price_from': price_from,
                    'price_to': price_to,
                    'company': company,
                    'city': city,
                    'link': link
                }
            else:
                return None  # Вакансия с указанным ID не найдена
    finally:
        connection.close()

