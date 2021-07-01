import requests
from bs4 import BeautifulSoup
import csv
import os
import sys


URL = 'https://auto.ria.com/uk/car/mercedes-benz/'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

def get_html(url, params=None):
    """
    This function return a html page for given url.
    """

    return requests.get(url, headers=HEADERS, params=params)

def get_content(html):
    """
    This function get important elements from parsed html and add them to dictionaries in list.
    """

    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='content')
    items_list = []

    for item in items:

        vin_code = item.find('span', class_='vin-code')
        if vin_code:
            vin = vin_code.get_text(strip=True)
        else:
            vin = 'Not found'

        items_list.append({
            'title': item.find('span', class_='blue bold').get_text(strip=True),
            'link': item.find('a', class_='address').get('href'),
            'price_usd': item.find('span', class_='bold green size22').get_text(strip=True) + ' $',
            'price_uah': item.find_next('span', class_='i-block').get_text(strip=True).replace('грн', ' ₴'),
            'city': item.find('li', class_='item-char view-location js-location').get_text(strip=True).replace('(від)', ''),
            'distance': item.find('li', class_='item-char js-race').get_text(strip=True),
            'fuel': item.find('li', class_='js-race').next_sibling.next_sibling.next_sibling.next_sibling.get_text(strip=True),
            'transmission': item.find('li', class_='js-race').next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text(strip=True),
            'vin-code': vin
        })
    return items_list

def get_pages_count(html):
    """
    This function get list of pages and return number last page if page has more than one page
    or return 1 if page is single.
    """

    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='mhide')

    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1

def parse():
    """
    This function get elements from all pages and add them to list.
    """

    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        count_pages = get_pages_count(html.text)
        print(f'I\'m find {count_pages} pages')
        print('---> Run parser...')

        for i in range(1, count_pages + 1):
            print(f'Parsing... {i}/{count_pages} pages')
            html = get_html(URL, params={'page': i})
            cars.extend(get_content(html.text))
        print(f'Got {len(cars)} cars')

        # Writing data from list to *.csv-file
        with open('Mersedes.csv', mode='w') as csv_file:
            fieldnames = ['title', 'link', 'price_usd', 'price_uah', 'city', 'distance', 'fuel', 'transmission', 'vin-code']

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()

            for line in cars:
                writer.writerow(line)
        # Cross-platform auto-running .csv-file
        if sys.platform == 'win32':
            os.startfile('Mersedes.csv')
        else:
            os.system('libreoffice Mersedes.csv')

    else:
        print('Something wrong... .')

parse()