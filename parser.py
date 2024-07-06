from main import db_insert
import requests
from bs4 import BeautifulSoup
import locale
import re

locale.setlocale(locale.LC_TIME, 'ru_RU')

def get_page(media_url):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.5845.888 YaBrowser/23.9.2.888 Yowser/2.5 Safari/537.36"
    }
    url = media_url
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    return soup

def all_vacancies(soup):
    all_titles = soup.find_all(class_="vacancy-search-item__card")
    inserted_ids = []
    for item in all_titles:
        title = item.find('span', class_='serp-item__title-link').text.strip()
        price_elem = item.find('span', class_ = lambda x: x and 'compensation-text' in x)
        price = price_elem.text.strip().replace('\u202f', '').replace('\xa0', ' ') if price_elem else 'Зарплата не указана'
        price_from_to = parse_price(price)
        price_from, price_to = int(price_from_to[0]), int(price_from_to[1])
        company = item.find('span', class_=lambda x: x and x.startswith('company-info-text')).text.strip()
        city = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.strip()
        link = item.find('a', class_='bloko-link').get('href')
        vacancy_id = db_insert(title, price, price_from, price_to, company, city, link)
        inserted_ids.append(vacancy_id)
    return inserted_ids


def vacancy_parser(search_string):
    all_inserted_ids = []
    for page in range(1):
        url = "https://hh.ru/search/vacancy?text=" + search_string + '&page=' + str(page)
        soup = get_page(url)
        inserted_ids = all_vacancies(soup)
        for id in inserted_ids:
            all_inserted_ids.append(id)
    return all_inserted_ids


def parse_price(price_text):
    price_from = 0
    price_to = 0
    price_text = price_text.replace('\u202F', '').replace(' ', '').replace(',', '.').replace('₽', '').strip()

    # Проверка формата "от 100000"
    match = re.match(r'от(\d+)', price_text)
    if match:
        price_from = int(match.group(1))
        price_to = 999999999
        return [price_from, price_to]

    # Проверка формата "10000 - 100000"
    match = re.match(r'(\d+)[–—-](\d+)', price_text)
    if match:
        price_from = int(match.group(1))
        price_to = int(match.group(2))
        return [price_from, price_to]

    # Проверка формата "до 100000"
    match = re.match(r'до(\d+)', price_text)
    if match:
        price_from = 0
        price_to = int(match.group(1))
        return [price_from, price_to]

    # Если не удалось распознать формат, возвращаем None, None
    return [price_from, price_to]

