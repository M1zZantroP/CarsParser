import csv
import time
import sys
import os
from selenium import webdriver
import requests
import lxml
from bs4 import BeautifulSoup


HEADERS = {
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

URL = input('Enter URL --->  ')


def get_html(url, params=None):
	return requests.get(url=url, params=params, headers=HEADERS).text


def get_paginations():
	otp = webdriver.FirefoxOptions()
	otp.add_argument('--headless')
	driver = webdriver.Firefox(executable_path='/home/mizzantrop/git_projects/CarsParser/geckodriver', options=otp)
	driver.get(URL)
	html = driver.page_source
	driver.close()
	driver.quit()

	soup = BeautifulSoup(html, 'lxml')
	items = soup.find_all('span', 'bold load')
	return int(items[0].text) // 10 + 1 if int(items[0].text) % 10 != 0 else int(items[0].text) // 10


def get_cars(html):
	soup = BeautifulSoup(html, 'lxml')
	items = soup.find_all('div', class_='content-bar')
	cars_list = []

	for i in items:
		if i.find('span', class_='label-vin'):
			if 'хххх' in i.find('span', class_='label-vin').find_next('span').get_text(strip=True):
				vin = 'Платний перегляд'
			else:
				vin = i.find('span', class_='label-vin').find_next('span').get_text(strip=True)
		else:
			vin = 'Відсутній'

		cars_list.append({
			'Назва': i.find('div', class_='ticket-title').text.strip(),
			'Ціна - $(USD)': int(i.find('span', class_='green').text.strip().replace(' ', '')),
			'Ціна - грн(UAH)': int(i.find('span', class_='i-block').text.strip().replace(' ', '')[:-3]),
			'Місто': i.find('li', class_='js-race').find_next('li').get_text(strip=True).replace('(від)', ''),
			'Пробіг': i.find('li', class_='js-race').get_text(strip=True),
			'Тип палива': i.find('li', class_='js-race').find_next('li').find_next('li').text.strip(),
			'Трансмісія': i.find('li', class_='js-race').find_next('li').find_next('li').find_next('li').text.strip(),
			'Учасник ДТП': '+' if i.find('span', class_='state _red') else '-',
			'VIN-код': vin,
			'Актуальність': i.find('div', class_='footer_ticket').get_text(strip=True),
			'Посилання': i.find('a', class_='address').get('href')
			})
	return cars_list


def parser():
	print('[INFO] Parser running... .')
	pagination = get_paginations()
	cars = []

	for i in range(pagination + 1):
		print(f'[INFO] Parsing #{i+1}/{pagination + 1} page')
		html = get_html(URL, params={'page': i, 'size': 20})
		cars.extend(get_cars(html))

	return cars


def get_file_name(url):
	temp = url.split('&')
	marka_id = ''
	model_id = ''
	for i in temp:
		if 'marka_id' in i:
			marka_id = i.split('=')[-1]
		elif 'model_id' in i:
			model_id = i.split('=')[-1]
	return f'cars_{marka_id}_{model_id}'


def main():
	start_time = time.time()
	cars = parser()
	file_name = get_file_name(URL)
	print(f'[INFO] Creating --> {file_name}.csv')
	with open(f'{file_name}.csv', 'w') as file:
		fieldnames = ['Назва', 'Ціна - $(USD)', 'Ціна - грн(UAH)', 'Місто', 'Пробіг', 'Тип палива',
					  'Трансмісія', 'Учасник ДТП', 'VIN-код', 'Актуальність', 'Посилання']

		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()

		for i in cars:
			writer.writerow(i)
		print('File saved successful!')

	# Opening file in Windows
	if sys.platform == 'win32':
		os.startfile(f'{file_name}.csv')

	print(f'\nFinished in {round(time.time() - start_time, 3)} sec.')
	print('Bye...')
