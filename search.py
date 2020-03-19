#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import time
from datetime import datetime
import argparse

import requests


# токен locationiq.com
TOKEN = 'pk.5fe3dc9c3b231365b0dbe8fb1b11a723'

# сервисный ключ доступа vk.com
token = ''

v = 5.103

E, R, G, Y, B = '\033[0m', '\033[31m', '\033[32m', '\033[33m', '\033[34m'
bp = '\n' + B + '-' * 75 + E
banner = B + '''

    ██╗   ██╗██╗  ██╗      ██████╗ ███████╗ ██████╗ 
    ██║   ██║██║ ██╔╝     ██╔════╝ ██╔════╝██╔═══██╗
    ██║   ██║█████╔╝█████╗██║  ███╗█████╗  ██║   ██║
    ╚██╗ ██╔╝██╔═██╗╚════╝██║   ██║██╔══╝  ██║   ██║
     ╚████╔╝ ██║  ██╗     ╚██████╔╝███████╗╚██████╔╝
      ╚═══╝  ╚═╝  ╚═╝      ╚═════╝ ╚══════╝ ╚═════╝ 
                                                    
    v.2 https://github.com/yevgen2020''' + E


def parse_vk(lat, long, start_time, end_time, radius, pr, size, fname=None):
    result = []
    if pr:
        proxies = {'http': 'socks5://127.0.0.1:8080',
                   'https': 'socks5://127.0.0.1:8080'}
    else:
        proxies = None

    params = {
        'lat': lat,
        'long': long,
        'start_time': start_time,
        'end_time': end_time,
        'radius': radius,
        'sort': 0,
        'count': 1000,
        'access_token': token,
        'v': v
    }

    r = requests.get('https://api.vk.com/method/photos.search', params=params,
                     proxies=proxies).json()

    count = r['response']['count']
    print(B + 'Всего: ' + E + str(count))
    for i in r['response']['items']:
        photo = ''

        if size == 'y':
            for s in i['sizes']:
                if s['type'] == 'w':
                    photo = i['sizes'][-4]['url']
            if not photo:
                photo = i['sizes'][-1]['url']

        else:
            for s in i['sizes']:
                if s['type'] == 'm':
                    photo = i['sizes'][0]['url']
            if not photo:
                photo = i['sizes'][-1]['url']

        date = i['date']
        if i['owner_id'] > 0:
            if fname:
                par = {
                    'user_ids': i['owner_id'],
                    'name_case': 'nom',
                    'access_token': token,
                    'v': v
                }
                response = requests.get('https://api.vk.com/method/users.get', params=par,
                                        proxies=proxies).json()
                name = response['response'][0]['first_name'] + ' ' + response['response'][0][
                    'last_name']
                time.sleep(0.5)
                result.append([photo, date, i['owner_id'], name])
            else:
                result.append([photo, date, i['owner_id']])
        else:
            continue

    return str(len(result)), result


def geoforward(q):
    data = {
        'key': TOKEN,
        'q': q,
        'format': 'json'
    }
    response = requests.get('https://eu1.locationiq.com/v1/search.php', params=data)
    if response.status_code != 200:
        return response.status_code
    response = response.json()
    return f"{response[0]['lat']}, {response[0]['lon']}"


if __name__ == '__main__':
    try:
        while True:
            print(banner)
            parser = argparse.ArgumentParser()
            parser.add_argument('-p', '--proxy', action='store_const', const=True,
                                help='SOCKS прокси слушает на 127.0.0.1:8080')
            if parser.parse_args().proxy:
                proxy = True
            else:
                proxy = False

            print(f'{bp}\nКоординаты в формате ДОЛГОТА, ШИРОТА Пример: {Y}55.753215, 37.622504{E}\n'
                  f'Адрес. Пример: {Y}россия москва новый арбат 19{bp}')
            while True:
                coordinates = input(f'{G}Координаты или адрес: {E}')
                if re.match(r'\d{1,2}\.\d{1,16},\s\d{1,2}\.\d{1,16}', coordinates):
                    break
                elif coordinates:
                    coordinates = geoforward(coordinates)
                    if re.match(r'\d{1,2}\.\d{1,16},\s\d{1,2}\.\d{1,16}', coordinates):
                        break
                else:
                    print(f'{R}Неверный фориат координат или locationiq вернул {coordinates}')
            place = 'Координаты: ' + coordinates
            coordinates = coordinates.split(', ')
            print(bp + '\nФормат ДД/ММ/ГГГГ ЧЧ:ММ Пример: ' + Y + '1/3/2020 08:05\n(время можно '
                                                                  'не '
                                                                  'указывать по умолчанию 00:00)' + bp)
            while True:
                input_end_date = input(f'{G}Конечные дата-время или [{E}Enter{G}] - текущие: {E}')
                if not input_end_date:
                    end_date = int(time.time())
                    break
                elif re.match(r'\d{2}/\d{2}/\d{4}\s\d\d:\d\d', input_end_date):
                    end_date = int(
                        time.mktime(datetime.strptime(input_end_date, '%d/%m/%Y %H:%M').timetuple()))
                    break
                elif re.match(r'\d{2}/\d{1,2}/\d{4}', input_end_date):
                    end_date = int(
                        time.mktime(datetime.strptime(input_end_date, '%d/%m/%Y').timetuple()))
                    break
                else:
                    print(f'{R}Неверный фориат даты-времени!')

            while True:
                input_start_date = input(f'{G}Начальные дата-время: {E}')
                if re.match(r'\d{1,2}/\d{1,2}/\d{4}\s\d\d:\d\d', input_start_date):
                    start_date = int(
                        time.mktime(datetime.strptime(input_start_date, '%d/%m/%Y %H:%M').timetuple()))
                    break
                elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', input_start_date):
                    start_date = int(
                        time.mktime(datetime.strptime(input_start_date, '%d/%m/%Y').timetuple()))
                    break
                else:
                    print(f'{R}Неверный фориат даты-времени!')

            while True:
                radius = input(f'{G}Радиус поиска в метрах [{E}10, 100, 800, 6000, 50000{G}]: {E}')
                if int(radius) in [10, 100, 800, 6000, 50000]:
                    break
                else:
                    print(f'{R}Неверный фориат радиуса!')

            size = input(f'{G}Разрешение фото [{E}y{G}]-большое или [{E}Enter{G}]-маленькое: {E}')
            family_name = input(f'{G}Фамилия имя нужны в выдаче?[{E}y{G}]-да, [{E}any key{G}]-нет: {E}')
            if family_name == 'y':
                fn = True
            else:
                fn = False

            print(B + '\nПарсинг...')
            items, res = parse_vk(*coordinates, start_date, end_date, radius, proxy, size,
                                  fname=fn)
            print(B + 'Отфильтрованых результатов: ' + E + items)
            if int(items) == 0:
                exit(0)
            place = place + '<br>Результатов: ' + items
            filename = str(time.time()).split('.')[0] + '.html'
            print(B + 'Файл: ' + E + os.getcwd() + '/' + filename + bp)
            file = open(filename, 'w')

            if size == 'y':
                colums = ' 400px 400px 400px;'
            else:
                colums = ' 200px 200px 200px 200px 200px 200px;'

            header = '<html><head><style type="text/css">' \
                     '.container {display: grid; grid-gap: 20px; grid-template-columns:' + colums +\
                     ' text-align: center;}' \
                     'a {text-decoration: none; color: black;}' \
                     'img {max-width: 400px; max-height: 300px; object-fit: cover;}' \
                     '</style></head><body>' \
                     '<h2 style="text-align: center">' + place + '</h2><div class="container">'

            file.write(header)

            for i in res:
                name_family = ''
                if len(i) == 4:
                    name_family = f'</br>{i[3]}'
                txt = datetime.utcfromtimestamp(int(i[1])).strftime('%d-%m-%Y %H:%M')
                link = 'https://vk.com/id' + str(i[2])
                to_write = f'\n\t\t\t<a target="_blank" rel="noopener" href="{link}"><img src="' \
                           f'{i[0]}" alt=""><br>{txt}{name_family}</a>'
                file.write(to_write)

            file.write('\n\t\t</div>\n\t</body>\n</html>')
            file.close()
            n = input(f'{G}Для продолжения нажмите [{E}любую клавишу{G}] или [{E}Ctrl+C{G}] для '
                      f'выхода{E}')

    except KeyboardInterrupt:
        print('\nОперация прервана. Выход...')
        exit(0)

    except Exception as err:
        print(err)
        exit(1)
