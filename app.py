import os
from flask import Flask, render_template, request, redirect, url_for
from parser import vacancy_parser
from main import get_vacancy_from_db

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query', '')  # Получаем значение из параметра 'query'

    # Вызываем ваш парсер с полученным запросом
    ids = vacancy_parser(search_query)
    print(ids)

    # Получаем данные из базы данных для каждого ID
    vacancies = []
    for id in ids:
        vacancy = get_vacancy_from_db(id)  # Функция, которая получает данные по ID из базы
        if vacancy:
            vacancies.append(vacancy)

    print(vacancies)

    # Получаем фильтры из GET-параметров
    salary_from = request.args.get('salary_from', '')
    salary_to = request.args.get('salary_to', '')
    city = request.args.get('city', '')

    # Фильтруем вакансии по полученным параметрам
    filtered_vacancies = []
    for vacancy in vacancies:
        if (not salary_from or vacancy['price_from'] >= int(salary_from)) and \
                (not salary_to or vacancy['price_to'] <= int(salary_to)) and \
                (not city or city.lower() in vacancy['city'].lower()):
            filtered_vacancies.append(vacancy)

    print(filtered_vacancies)
    return render_template('results.html', vacancies=filtered_vacancies)


if __name__ == '__main__':
    app.run(debug=True)