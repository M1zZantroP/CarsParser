import time

import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import lxml


URL = input('Enter URL --->  ')
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def get_html(url, params=None):
    return requests.get(URL, params=params, headers=HEADERS).text


def get_cars(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', class_='proposition')
    cars_list = []

    for i in items:
        if i.find(class_='badge--checked'):
            vin = 'Перевірений'
        else:
            vin = 'Відсутній'
        cars_list.append({
            'Назва': i.find('span', class_='link').text.strip() + ' ' + i.find('span', class_='link').find_next().get_text(strip=True),
            'Ціна - $(USD)': int(i.find('span', class_='green').text.strip().replace(' ', '')[:-1]),
            'Ціна - грн(UAH)': int(i.find('span', class_='size16').text.strip().replace(' ', '')[:-3]),
            'Місто': i.find('span', class_='region').get_text(strip=True),
            'Тип палива': i.find('span', class_='region').find_next('span').text.strip().replace('• ', '(') + ')',
            'Трансмісія': i.find('span', class_='region').find_next(class_='item').find_next(class_='item').text.strip(),
            'Тип приводу': i.find('span', class_='region').find_next(class_='item').find_next(class_='item').find_next(class_='item').text.strip(),
            'Пропозиції': '; '.join([x.text.strip().replace(' • ', ' - ') for x in i.find_all(class_='badge--grey')]),
            'VIN-код': vin,
            'Деталі': i.find(class_='proposition_badges').find_next('div').get_text(strip=True),
            'Фото': i.find('img', class_='m-auto').get('src'),
            'Посилання': 'https://auto.ria.com' + i.find('a').get('href')
        })
    return cars_list


def get_max_pagination(html):
    soup = BeautifulSoup(html, 'lxml')
    paginations = soup.find_all(class_='page-link')

    return int(paginations[-2].get_text())


def parser():
    print('[INFO] Parser running... .')
    html = get_html(URL)
    pagination = get_max_pagination(html)
    cars = []

    for i in range(1, pagination + 1):
        print(f'[INFO] Parsing {i}/{pagination} page')
        html = get_html(URL, params={'page': i})
        temp = get_cars(html)
        cars.extend(temp)

    return cars


if __name__ == '__main__':
    start_time = time.time()
    cars = parser()
    print('[INFO] Creating --> cars.csv')
    keywords = ['Назва', 'Ціна - $(USD)', 'Ціна - грн(UAH)', 'Місто', 'Тип палива', 'Трансмісія',
                'Тип приводу', 'Пропозиції', 'VIN-код', 'Деталі', 'Фото', 'Посилання']
    with open('cars.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(keywords)
        for i in cars:
            writer.writerow(list(i.values()))
    print('File save successful!')

    print(f'Finished in {round(time.time() - start_time, 3)} sec.')
    print('Bye...')